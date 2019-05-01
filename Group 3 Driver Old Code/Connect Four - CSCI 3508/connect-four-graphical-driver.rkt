#lang racket/gui

(require json)

;;; Define grid dimensions.
(define HEIGHT 6)
(define WIDTH 7)

;;; These will eventually be command line arguments.
(define exe-1 "C:\\Program Files\\Racket\\Racket.exe")
(define args-1 '("connect-four-naive.rkt"))
(define exe-2 "C:\\Program Files\\Python36.\\python.exe")
(define args-2 '("connect-four-naive.py"))

;;; (new-grid grid move player) -> (listof (listof (integer-in 0 2)))
;;;   grid : (listof (listof (integer-in 0 2)))
;;;   move : exact-positive-integer?
;;;   player : (integer-in 1 2)
;;; Returns a new grid with the specified move by player.
(define (new-grid grid move player)
  (for/list ((col (in-list grid))
             (i (in-naturals)))
    (cond ((= i move)
           (define n (count zero? col))
           (when (= n 0)
             (error 'new-grid
                    "player ~a move ~s is illegal" player move))
           (append (make-list (- n 1) 0) (list player) (drop col n)))
          (else
           col))))

;;; (winner? grid player) -> boolean?
;;;   grid : (listof (listof (integer-in 0 2)))
;;;   player : (integer-in 1 2)
;;; Returns true of the grid is a win for player.
(define (winner? grid player)
  (define vgrid
    (for/vector #:length WIDTH ((col (in-list grid)))
      (for/vector #:length HEIGHT ((cell (in-list col)))
        cell)))
  (let/ec exit
    (for* ((i (in-range WIDTH))
           (j (in-range HEIGHT)))
      ;; Check for four in a row diagonally up.
      (when (and (<= i (- WIDTH 4))
                 (>= j 3)
                 (for/and ((k (in-range 4)))
                   (= player (vector-ref (vector-ref vgrid (+ i k)) (- j k)))))
        (exit #t))
      ;; Check for four in a row across.
      (when (and (<= i (- WIDTH 4))
                 (for/and ((k (in-range 4)))
                   (= player (vector-ref (vector-ref vgrid (+ i k)) j))))
        (exit #t))
      ;; Check for four in a row diagonally down.
      (when (and (<= i (- WIDTH 4))
                 (<= j (- HEIGHT 4))
                 (for/and ((k (in-range 4)))
                   (= player (vector-ref (vector-ref vgrid (+ i k)) (+ j k)))))
        (exit #t))
      ;; Check for four in a row down.
      (when (and (<= j (- HEIGHT 4))
                 (for/and ((k (in-range 4)))
                   (= player (vector-ref (vector-ref vgrid i) (+ j k)))))
        (exit #t)))
    #f))

;;; (grid-print grid move) -> void?
;;;   grid : (listof (listof (integer-in 0 2)))
;;;   move : exact-positive-integer?
;;; Prints the grid. Not used in the graphical version.
(define (grid-print grid move)
  (printf "--- Move ~a ---~n" move)
  (for ((j (in-range HEIGHT)))
    (for ((i (in-range WIDTH)))
      (define cell (list-ref (list-ref grid i) j))
      (printf "~a " (if (= cell 0) " " cell)))
    (printf "~n")))

;;; (main) -> void?
(define (main)
  ;; Create forts for standard error (text) files.
  (define stderr-1 (open-output-file "connect-four-stderr-1.txt"
                                     #:mode 'text #:exists 'replace))
  (define stderr-2 (open-output-file "connect-four-stderr-2.txt"
                                     #:mode 'text #:exists 'replace))
  ;; Create the subprocesses.
  (define-values (process-1 process-stdout-1 process-stdin-1 process-stderr-1)
    (apply subprocess #f #f stderr-1 exe-1
           (append args-1 `("--player" "1"
                            "--width" ,(number->string WIDTH)
                            "--height" ,(number->string HEIGHT)))))
  ;(sleep .1) ; So process random numbers aren't synchronized.
  (define-values (process-2 process-stdout-2 process-stdin-2 process-stderr-2)
    (apply subprocess #f #f stderr-2 exe-2
           (append args-2 `("--player" "2"
                            "--width" ,(number->string WIDTH)
                            "--height" ,(number->string HEIGHT)))))
  ;; Create vector of standard ports.
  (define process-stdout (vector #f process-stdout-1 process-stdout-2))
  (define process-stdin (vector #f process-stdin-1 process-stdin-2))
  (define process-stderr (vector #f  stderr-1 stderr-2))
  ;; Loop alternately calling the players.
  (let/ec exit
    (let loop ((n 1)
               (player (if (<= (random) 0.5) 1 2))
               (grid (for/list ((col (in-range WIDTH)))
                       (for/list ((row (in-range HEIGHT)))
                         0))))
      (send message set-label (format "Move ~a player ~a" n player))
      ;; Construct the percept as a jsexpr.
      (define percept-jsexpr
        (hasheq 'grid grid))
      ;; Send the percept to the appropriate player.
      (displayln (jsexpr->string percept-jsexpr) (vector-ref process-stdin player))
      (flush-output (vector-ref process-stdin player))
      ;; Get the action from the appropriate player.
      (define action-json (read-line (vector-ref process-stdout player)))
      (when (eof-object? action-json)
        (exit))
      (define action-jsexpr (string->jsexpr action-json))
      ;; Process the action.
      (define move (hash-ref action-jsexpr 'move))
      (define next-grid (new-grid grid move player))
      ;(grid-print next-grid n)
      (draw-move grid move player)
      (sleep/yield 0.1)
      (cond ((winner? next-grid player)
             (send message set-label (format "Player ~a wins" player)))
            ((= n (* HEIGHT WIDTH))
             (send message set-label "Draw"))
            (else
             (loop (+ n 1) (if (= player 1) 2 1) next-grid)))))
  ;; Close the ports.
  (for ((player (in-range 1 3)))
    (close-output-port (vector-ref process-stdin player))
    (close-input-port (vector-ref process-stdout player))
    (close-output-port (vector-ref process-stderr player)))
  ;;
  (send run-button enable #t))

;;; Graphics

(define CELL-SIZE 72)

(define mask #f)
(define board #f)

(define (initialize-board)
  ;; Create the mask to draw the board - i.e., the holes.
  (set! mask (make-monochrome-bitmap (* WIDTH CELL-SIZE) (* HEIGHT CELL-SIZE)))
  (define mask-dc (send mask make-dc))
  (send mask-dc set-smoothing 'aligned)
  (send mask-dc set-background "black")
  (send mask-dc clear)
  (send mask-dc set-pen "white" 1 'transparent)
  (send mask-dc set-brush "white" 'solid)
  (for ((i (in-range HEIGHT)))
    (for ((j (in-range WIDTH)))
      (define x (+ (* j CELL-SIZE) 5))
      (define y (+ (* i CELL-SIZE) 5))
      (define size (- CELL-SIZE 10))
      (send mask-dc draw-ellipse x y size size)))
  ;;; Create the solid bitmap for the board.
  (set! board (make-bitmap (* WIDTH CELL-SIZE) (* HEIGHT CELL-SIZE)))
  (define board-dc (send board make-dc))
  (send board-dc set-smoothing 'aligned)
  (send board-dc set-background "blue")
  (send board-dc clear))

(initialize-board)

;;; (draw-move grid move player) -> void?
;;;   grid : (listof (listof (integer-in 0 2)))
;;;   move : exact-nonnegative-integer?
;;;   player : (integer-in 1 2)
;;; Animates moves.
(define (draw-move grid move player)
  (define canvas-dc (send canvas get-dc))
  (send canvas-dc set-smoothing 'aligned)
  ;; Create a bitmap for the previous grid
  (define bitmap (make-bitmap (* WIDTH CELL-SIZE) (* HEIGHT CELL-SIZE)))
  (define bitmap-dc (send bitmap make-dc))
  (send bitmap-dc clear)
  (send bitmap-dc set-smoothing 'aligned)
  (for ((column (in-list grid))
        (j (in-naturals)))
    (for ((cell (in-list column))
          (i (in-naturals)))
      (define x (* j CELL-SIZE))
      (define y (* i CELL-SIZE))
      (unless (= cell 0)
        (case cell
          ((1) (send bitmap-dc set-pen "black" 1 'transparent)
               (send bitmap-dc set-brush "black" 'solid))
          ((2) (send bitmap-dc set-pen "red" 1 'transparent)
               (send bitmap-dc set-brush "red" 'solid)))
        (send bitmap-dc draw-ellipse x y CELL-SIZE CELL-SIZE))))
  ;; Animate the move
  (case player
    ((1) (send canvas-dc set-pen "black" 1 'transparent)
         (send canvas-dc set-brush "black" 'solid))
    ((2) (send canvas-dc set-pen "red" 1 'transparent)
         (send canvas-dc set-brush "red" 'solid)))
  (define x (* move CELL-SIZE))
  (define n (* (- (count zero? (list-ref grid move)) 1) CELL-SIZE))
  (for ((y (in-range 0 (+ n 1) (/ CELL-SIZE 4))))
    (send canvas-dc suspend-flush)
    (send canvas-dc draw-bitmap bitmap 0 0)
    (send canvas-dc draw-ellipse x y CELL-SIZE CELL-SIZE)
    (send canvas-dc draw-bitmap board 0 0 'solid
          (send the-color-database find-color "blue")
          mask)
    (send canvas-dc resume-flush)
    (sleep/yield 1/120)))

;;; Graphic elements

;;; Frame
(define frame
  (instantiate frame%
    ("Connect Four")
    (style '(no-resize-border))))

;;; Menu Bar and Items
(define menu-bar
  (instantiate menu-bar%
    (frame)))

(define file-menu
  (instantiate menu%
    ("&File" menu-bar)))

(define exit-menu-item
  (instantiate menu-item%
    ("E&xit" file-menu)
    (callback
     (lambda (menu-item event)
       (exit)))))

(define edit-menu
  (instantiate menu%
    ("&Edit" menu-bar)))

(define preferences-menu-item
  (instantiate menu-item%
    ("Preferences..." edit-menu)
    (callback
     (lambda (menu-item event)
       (send dialog show #t)))))

;;; Preferences Dialog
(define dialog
  (instantiate dialog%
    ("Preferences" frame)))

(define grid-group-box-panel
  (instantiate group-box-panel%
    ("Grid" dialog)
    (alignment '(left top))))

(define width-text-field
  (instantiate text-field%
    ("Width" grid-group-box-panel)
    (init-value (~a WIDTH))))

(define height-text-field
  (instantiate text-field%
    ("Height" grid-group-box-panel)
    (init-value (~a HEIGHT))))

(define cell-size-text-field
  (instantiate text-field%
    ("Cell Size" grid-group-box-panel)
    (init-value (~a CELL-SIZE))))

(define player-1-group-box-panel
  (instantiate group-box-panel%
    ("Player 1 Program" dialog)
    (alignment '(left top))))

(define player-1-horizontal-panel
  (instantiate horizontal-panel%
    (player-1-group-box-panel)))

(define player-1-exe-text-field
  (instantiate text-field%
    ("Executable" player-1-horizontal-panel)
    (init-value (~a exe-1))
    (min-width 400)))

(define player-1-exe-browse-button
  (instantiate button%
    ("..." player-1-horizontal-panel)
    (callback
     (lambda (button event)
       (define file (get-file "Select Player 1 Player Program"))
       (when file
         (define file-name (path->string file))
         (send player-1-exe-text-field set-value file-name)
         (send player-1-exe-text-field refresh))))))

(define player-1-args-text-field
  (instantiate text-field%
    ("Arguments" player-1-group-box-panel)
    (init-value (~s args-1))
    (min-width 400)))

(define player-2-group-box-panel
  (instantiate group-box-panel%
    ("Player 2 Program" dialog)
    (alignment '(left top))))

(define player-2-horizontal-panel
  (instantiate horizontal-panel%
    (player-2-group-box-panel)))

(define player-2-exe-text-field
  (instantiate text-field%
    ("Executable" player-2-horizontal-panel)
    (init-value (~a exe-2))
    (min-width 400)))

(define player-2-exe-browse-button
  (instantiate button%
    ("..." player-2-horizontal-panel)
    (callback
     (lambda (button event)
       (define file (get-file "Select Player 1 Player Program"))
       (when file
         (define file-name (path->string file))
         (send player-2-exe-text-field set-value file-name)
         (send player-2-exe-text-field refresh))))))

(define player-2-args-text-field
  (instantiate text-field%
    ("Arguments" player-2-group-box-panel)
    (init-value (~s args-2))
    (min-width 400)))

(define button-bar
  (instantiate horizontal-panel%
    (dialog)
    (alignment '(center center))))

(define cancel-button
  (instantiate button%
    ("Cancel" button-bar)
    (callback
     (lambda (button event)
       (send dialog show #f)))))

(define ok-button
  (instantiate button%
    ("Ok" button-bar)
    (callback
     (lambda (button event)
       (set! WIDTH (string->number (send width-text-field get-value)))
       (set! HEIGHT (string->number (send height-text-field get-value)))
       (set! CELL-SIZE (string->number (send cell-size-text-field get-value)))
       (set! exe-1 (send player-1-exe-text-field get-value))
       (set! args-1 (read (open-input-string (send player-1-args-text-field get-value))))
       (set! exe-2 (send player-2-exe-text-field get-value))
       (set! args-2 (read (open-input-string (send player-2-args-text-field get-value))))
       (send canvas min-width (* WIDTH CELL-SIZE))
       (send canvas min-height (* HEIGHT CELL-SIZE))
       (send (send canvas get-dc) clear)
       (initialize-board)
       (send dialog show #f)))))

;;; Message - game state - move, wins, etc.
(define message
  (instantiate message%
    ("" frame)
    (stretchable-width #t)))

;;; Canvas - game grid
(define canvas
  (instantiate canvas%
    (frame)
    (min-width (* WIDTH CELL-SIZE))
    (min-height (* HEIGHT CELL-SIZE))
    (stretchable-width #f)
    (stretchable-height #f)))

;;; Run Button
(define run-button
  (instantiate button%
    ("Run" frame
           (lambda (b e)
             (send run-button enable #f)
             (main)))))

;;; Show the frame.
(send frame show #t)
