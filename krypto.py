#!/usr/bin/python
import sys, random,operator,re
class deck:
  '''

  The Krypto deck consists of 56 cards: three each of numbers 1-6, four each of 
  the numbers 7-10, two each of 11-17, one each of 18-25.

 [1, 2, 3, 4, 5, 6, 1, 2, 3, 4, 5, 6, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 7, 8, 9,     10, 7, 8, 9, 10, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 11, 12, 13, 14, 
  15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25]
  '''
  cards = range(1,7) * 3 + range(7,11)*4 + range(11,18)*2 + range(18,26)

  def deal(self):
      return random.sample(self.cards,6)

class kryptobot:
  def __init__(self,players):
    self.players = players
    self.d = deck()
    self.cards = self.d.deal()
    self.hand = 1
    self.streak = 0
    self.previous_winner = None
    self.score_pad = dict(zip(players,[[0]for x in range(len(players))]))
    print self.score_pad.keys()
    self.print_cards()

  def scores(self):
    for name,score in sorted(self.score_pad.iteritems(),key=operator.itemgetter(0)):
      yield name,score

  def __str__(self):
    namemaxlen = max(len(x) for x in self.players) + 1 
    handlen = self.hand*8 + 9 # for the |
    # header
    # .-----------------------.
    # |      | Hand X | Total |
    out = "."+"-"*((namemaxlen) + handlen)+".\n"
    out += "|"+" "*namemaxlen+"| "
    out += "".join(["Hand {} | ".format(d) for d in range(1,self.hand+1)])+ "Total |\n"

    out += "|"+"-"*((namemaxlen) + handlen)+"|\n"
    # scores
    for name,scores in self.scores():
      out += "|"+name.ljust(namemaxlen)+"|"
      for score in scores:
        out += str(score).center(8) + "|"
      out += str(sum(scores)).center(7)+"|\n"
        
    # footer
    # '---------'
    out += "'"+"-"*((namemaxlen) + (self.hand*8)+9)+"'\n"
    return out

  def check_solution(self, player, solution):
    ''' 
    *** solution should be a string representing an infix expression 
    *** that allows paratheses where each card that was delt was used once
    *** and only once to equal the objective card.
    *** 
    *** Cards: 1, 3, 7, 1 8 = 1
    *** "((((A + B) + C) + D) + E)"


    *** Will use the "Shunting Yard Algorithm"
    *** http://en.wikipedia.org/wiki/Shunting-yard_algorithm#The_algorithm_in_detail
    '''

    #tokenize string.   
    tokens = re.findall(r"[\(\)\d\+\-\*\/]",solution)
    # convert infix to postfix
    operators = {
      '+' : (0,"left"),
      '-' : (0,"left"),
      '*' : (1,"left"),
      '/' : (1,"left"),
    }
    out = []
    stack = []
    print tokens
    for token in tokens:
        if token.isdigit():
          out.append(token)
        if token in operators.keys():
          while len(stack) !=0 and stack[-1] in operators.keys() and \
                (operators[token][1] == "left" and \
                operators[token][0] <= operators[stack[-1]][0] or \
                operators[token][0] < operators[stack[-1]][0]):
            out.append(stack.pop())
          stack.append(token)
        elif token == '(':
          stack.append(token)
        elif token == ')':
          while len(stack) > 0 and stack[-1] != "(":
              out.append(stack.pop())
          if len(stack) == 0:
            return # Error mismatched.
          if stack[-1] == "(":
            stack.pop()
    while len(stack):
      if stack[-1] == ")" or stack[-1] == "(":
        return # error
      out.append(stack.pop())
    print out
    ##########
    # Evaluate the expression
    ##########
    stack = []
    for o in out:
      if o in operators.keys():
        a = stack.pop()
        b = stack.pop()
        stack.append(self.calc(a,o,b))
      elif o.isdigit():
        stack.append(o)
    print stack
    if len(stack) > 1:
      print "Too many values on the stack!"
      return # too many values on stack
    correct = (self.cards[5] == int(stack.pop()))
    if correct: print "Correct!" 
    else: print "Not Correct!"


   
    self.score_hand(player,correct)
    self.deal_next()

  def calc(self,a,op,b):
    a = int(a)
    b = int(b)
    if op == "+":
      return a + b
    if op == "-":
      return a - b
    if op == "/":
      return a / b
    if op == "*":
      return a * b
  def score_hand(self,player,correct):
    ''':
    *** Score Keeping Rules:
    *** Ten hands of Krypto equal one game. Players receive one point for each 
    *** "Krypto". Players receive double their previous hand score each time they 
    *** "Krypto" repetitively in sequence. A score returns to "1" when sequence is 
    *** broken. When players "Krypto" in error, they receive a minus one (-1) in the 
    *** score box for that hand. They are also eliminated from play of that hand 
    *** only and the hand is re-dealt for the remaining players. All players are then 
    *** eligible to score the next hand unless another error in "Kryptoing" occurs.
    '''
    if correct: 
      previous_score = self.score_pad[player][self.hand-1]
      if player == self.previous_winner:
        self.streak += 1
        score = self.streak * previous_score
      else:
        score = 1
        self.streak = 0
      self.previous_winner = player
    else:
        score = -1
        self.streak = 0
    self.score_pad[player].append(score) 

  def print_cards(self):
    print " Cards: ",",".join([str(x) for x in self.cards])

  def deal_next(self):
    self.cards = self.d.deal()
    self.hand += 1

if __name__ == "__main__":
  p = ["Fred","JoeBob","LongAssName","bo"]
  k = kryptobot(p)
  k.print_cards()
  print str(k)
  k.check_solution("Fred","(3 * 4)+(8+2)")
  
  print str(k)

