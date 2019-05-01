#lang racket

(require json)

;;; Define grid dimensions.
(define HEIGHT 6)
(define WIDTH 7)

;;; These will eventually be command line arguments.
;;; The defaults play the naive player program against itself. But, it is
;;; specified two different ways: (1) Player 1 uses the compiled naive player
;;; program, and (2) Player 2 uses the naive player source code interpreted by
;;; Racket.
(define exe-1 "C:\\Program Files\\Racket\\Racket.exe")
(define args-1 '("connect-four-scoring-2.rkt"))
(define exe-2 "C:\\Program Files\\Racket\\Racket.exe")
(define args-2 '("connect-four-scoring-2.rkt"))

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
;;; Prints the grid.
(define (grid-print grid move)
  (printf "--- Move ~a ---~n" move)
  (for ((j (in-range HEIGHT)))
    (for ((i (in-range WIDTH)))
      (define cell (list-ref (list-ref grid i) j))
      (printf "~a " (if (= cell 0) " " cell)))
    (printf "~n")))

;;; (play first-player print-game?) -> ((integer-in 1 2)
;;;                                     (or/c (integer-in 0 2) #f)
;;;                                     exact-nonnegative-integer?)
;;;   first-player : (integer-in 1 2) = (if (<= (random) 0.5) 1 2)
;;;   print-game? : boolean? = #t
;;; Plays a game of Connect Four between two players with the specified player
;;; making the first move. Returns three values: (1) the first player; (2) the
;;; outcome of the game: 0 - draw, 1 - Player 1 wins, 2 - Player 2 wins, #f - an
;;; error occurred; and (3) the number of moves.
(define (play (first-player (if (<= (random) 0.5) 1 2)) (print-game? #t))
  ;; Create forts for standard error (text) files
;  (define stderr-1 (open-output-file "connect-four-stderr-1.txt"
;                                     #:mode 'text #:exists 'replace))
;  (define stderr-2 (open-output-file "connect-four-stderr-2.txt"
;                                     #:mode 'text #:exists 'replace))
  ;; Create the subprocesses
  (define-values (process-1 process-stdout-1 process-stdin-1 process-stderr-1)
    (apply subprocess #f #f #f exe-1 args-1))
  (define-values (process-2 process-stdout-2 process-stdin-2 process-stderr-2)
    (apply subprocess #f #f #f exe-2 args-2))
  ;; Create vector of standard ports.
  (define process-stdout (vector #f process-stdout-1 process-stdout-2))
  (define process-stdin (vector #f process-stdin-1 process-stdin-2))
  (define process-stderr (vector #f  process-stderr-1 process-stderr-2))
  ;; Loop alternately calling the players
  (define-values (outcome moves)
    (let/ec exit
      (let loop ((move 1)
                 (player first-player)
                 (grid (for/list ((col (in-range WIDTH)))
                         (for/list ((row (in-range HEIGHT)))
                           0))))
        ;; Construct the percept as a jsexpr
        (define percept-jsexpr
          (hasheq 'player player
                  'height HEIGHT
                  'width WIDTH
                  'grid grid))
        ;; Send the percept to the appropriate player
        (displayln (jsexpr->string percept-jsexpr) (vector-ref process-stdin player))
        (flush-output (vector-ref process-stdin player))
        ;; Get the action from the appropriate player
        (define action-json (read-line (vector-ref process-stdout player)))
        (when (eof-object? action-json)
          (when print-game?
            (printf "Unexpected EOF from player ~a~n" player))
          (exit #f move))
        (define action-jsexpr (string->jsexpr action-json))
        ;; Process the action
        (define next-grid (new-grid grid (hash-ref action-jsexpr 'move) player))
        (when print-game?
          (grid-print next-grid move))
        (cond ((winner? next-grid player)
               (when print-game?
                 (printf "Player ~a wins in ~a moves~n" player move))
               (values player move))
              ((= move (* HEIGHT WIDTH))
               (when print-game?
                 (printf "Draw in ~a moves~n" move))
               (values 0 move))
              (else
               (loop (+ move 1) (if (= player 1) 2 1) next-grid))))))
  ;; Close the ports
  (for ((player (in-range 1 3)))
    (close-output-port (vector-ref process-stdin player))
    (close-input-port (vector-ref process-stdout player))
    (close-input-port (vector-ref process-stderr player)))
  ;; Return the results
  (values first-player outcome moves))

;;; Head-to-head play with statistics
(define (head-to-head (n 10))
  ;; N games with Player 1 as first player
  (define player-1-results
    (for/list ((i (in-range n)))
      (call-with-values (lambda () (play 1 #f)) list)))
  ;; N games with Player 2 as first player
  (define player-2-results
    (for/list ((i (in-range n)))
      (call-with-values (lambda () (play 2 #f)) list)))
  ;; Summarize results
  (define n-games (* n 2))
  (define n-draws
    (+ (count (lambda (result) (= (second result) 0)) player-1-results)
       (count (lambda (result) (= (second result) 0)) player-2-results)))
  (define n-wins-1
    (+ (count (lambda (result) (= (second result) 1)) player-1-results)
       (count (lambda (result) (= (second result) 1)) player-2-results)))
  (define n-wins-2
    (+ (count (lambda (result) (= (second result) 2)) player-1-results)
       (count (lambda (result) (= (second result) 2)) player-2-results)))
  (define n-wins-1-first
    (count (lambda (result) (= (second result) 1)) player-1-results))
  (define n-wins-2-first
    (count (lambda (result) (= (second result) 2)) player-2-results))
  (printf "A total of ~a games were played.~n" n-games)
  (printf "A total of ~a games were draws.~n" n-draws)
  (printf "Player 1 won ~a games total.~n" n-wins-1)
  (printf "Player 2 won ~a games total.~n" n-wins-2)
  (printf "Player 1 won ~a games when they moved first.~n" n-wins-1-first)
  (printf "Player 2 won ~a games when they moved first.~n" n-wins-2-first)
  (cond ((= n-wins-1 n-games)
         (printf "Player 1 won every game.~n"))
        ((= n-wins-2 n-games)
         (printf "Player 2 won every game.~n"))
        ((and (= n-wins-1-first n) (= n-wins-2-first n))
         (printf "Players 1 and 2 won every game where they moved first.~n"))
        ((= n-wins-1-first n)
         (printf "Player 1 won every game where they moved first.~n"))
        ((= n-wins-2-first n)
         (printf "Player 2 won every game where they moved first.~n"))
        (else
         (printf "There were mixed results.~n")))
)

;;; Start the program
(play)
