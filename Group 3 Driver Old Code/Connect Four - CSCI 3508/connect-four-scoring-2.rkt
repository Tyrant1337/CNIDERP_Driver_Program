#lang racket

(require json
         racket/os)

(define player (make-parameter 1))
(define width (make-parameter 7))
(define height (make-parameter 6))

(define (other-player player)
  (if (= player 1) 2 1))

;;; (valid-moves grid) -> (listof exact-nonnegative-integer?)
;;;   grid : (listof (listof exact-nonnegative-integer?))
;;; Returns a list of the valid moves - that is columns that aren't full.
(define (valid-moves grid)
  (for/fold ((moves '()))
            ((col (in-list grid))
             (i (in-naturals)))
    (cond ((= 0 (first col))
           (append moves (list i)))
          (else
           moves))))

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

(define (score-four four)
  #;(fprintf (current-error-port) "(score-four ~a)~n" four)
  (define n (- 4 (count zero? four)))
  (cond ((= n 4)
         +inf.0)
        (else
         (expt n 2))))

;;; (score-grid grid player) -> boolean?
;;;   grid : (listof (listof (integer-in 0 2)))
;;;   player : (integer-in 1 2)
;;; Returns true of the grid is a win for player.
(define (score-grid grid player)
  #;(fprintf (current-error-port) "(score-grid ~a ~a)~n" grid player)
  (define vgrid
    (for/vector #:length (width) ((col (in-list grid)))
      (for/vector #:length (height) ((cell (in-list col)))
        cell)))
  (define other (other-player player))
  (define score 0)
  (for* ((i (in-range (width)))
         (j (in-range (height))))
    ;; Check for four in a row diagonally up.
    (when (and (<= i (- (width) 4))
               (>= j 3)
               (not (for/or ((k (in-range 4)))
                      (= other (vector-ref (vector-ref vgrid (+ i k)) (- j k))))))
      (define four (for/list ((k (in-range 4))) (vector-ref (vector-ref vgrid (+ i k)) (- j k))))
      (set! score (+ score (score-four four))))
    ;; Check for four in a row across.
    (when (and (<= i (- (width) 4))
               (not (for/or ((k (in-range 4)))
                      (= other (vector-ref (vector-ref vgrid (+ i k)) j)))))
      (define four (for/list ((k (in-range 4))) (vector-ref (vector-ref vgrid (+ i k)) j)))
      (set! score (+ score (score-four four))))
    ;; Check for four in a row diagonally down.
    (when (and (<= i (- (width) 4))
               (<= j (- (height) 4))
               (not (for/or ((k (in-range 4)))
                      (= other (vector-ref (vector-ref vgrid (+ i k)) (+ j k))))))
      (define four (for/list ((k (in-range 4))) (vector-ref (vector-ref vgrid (+ i k)) (+ j k))))
      (set! score (+ score (score-four four))))
    ;; Check for four in a row down.
    (when (and (<= j (- (height) 4))
               (not (for/or ((k (in-range 4)))
                      (= other (vector-ref (vector-ref vgrid i) (+ j k))))))
      (define four (for/list ((k (in-range 4))) (vector-ref (vector-ref vgrid i) (+ j k))))
      (set! score (+ score (score-four four))))
    #;(fprintf (current-error-port) "i = ~a, j= ~a, score = ~a~n" i j score))
  #;(fprintf (current-error-port) "score = ~a~n" score)
  score)

(define (score-moves grid)
  #;(fprintf (current-error-port) "(score-moves ~a)~n" grid)
  (define moves (valid-moves grid))
  (for/list ((i (in-range (width))))
    (cond ((memq i moves)
           (define new (new-grid grid i (player)))
           (- (score-grid new (player))
              (score-grid new (other-player (player)))))
          (else
           -inf.0))))

(define (select-move scores)
  (define max-score -inf.0)
  (define moves '())
  (for ((score (in-list scores))
        (i (in-naturals)))
    (cond ((= score -inf.0)
           (void))
          ((> score max-score)
           (set! max-score score)
           (set! moves (list i)))
          ((= score max-score)
           (set! moves (cons i moves)))))
  (list-ref moves (random (length moves))))

;;; (play) -> void?
(define (play)
  (displayln "Connect Four" (current-error-port))
  (fprintf (current-error-port) "  player = ~a~n" (player))
  (fprintf (current-error-port) "  width = ~a~n" (width))
  (fprintf (current-error-port) "  height = ~a~n" (height))
  ;; Seed the current pseudo-random number generator with a value that will be
  ;; different for different player programs
  (random-seed (modulo (abs (* (getpid) (current-milliseconds)))
                       (sub1 (expt 2 31))))
  ;; Process the precepts.
  (for ((json (in-lines)))
    (displayln json (current-error-port))
    (define precept (string->jsexpr json))
    (define grid (hash-ref precept 'grid))
    ;; Score the moves.
    (define scores (score-moves grid))
    (displayln scores (current-error-port))
    ;; Choose one of the 'best'.
    (define move (select-move scores))
    ;; Return the action.
    (define action
      (hasheq 'move move))
    (define action-json (jsexpr->string action))
    (displayln action-json (current-error-port))
    (displayln action-json)
    (flush-output)))

;;; (main) -> void?
(define (main)
  (command-line
   #:program "connect-four-scoring"
   #:once-each
   ("--player"
    p
    "player number"
    (player (string->number p)))
   ("--width"
    w
    "grid width (number of columns)"
    (width (string->number w)))
   ("--height"
    h
    "grid height (number of rows)"
    (height (string->number h)))
   #:args ()
   (play)))

;;; Start the program.
(main)
