#!/usr/bin/python
import sys, random,operator 
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
    d = deck()
    self.cards = d.deal()
    self.hand = 2
    self.score_pad = dict(zip(players,[[0]for x in range(len(players))]))
    print self.score_pad.keys()
    self.print_cards()

  def scores(self):
    for name,score in sorted(self.score_pad.iteritems(),key=operator.itemgetter(0)):
      yield name,score

  def print_scores(self):
    maxlen = max(len(x) for x in self.players) + 1 
    # header
    # .-----------------------.
    # |      | Hand X | Total |
    print "."+"-"*((maxlen) + (self.hand*8)+9)+"."
    print "|"+" "*maxlen+"|",
    print "".join(["Hand {} | ".format(d) for d in range(1,self.hand+1)])+ \
          "Total |"

    print "|"+"-"*((maxlen) + (self.hand*8)+9)+"|"
    # scores
    for name,scores in self.scores():
      sys.stdout.write("|"+name.ljust(maxlen)+"|")
      for score in scores:
        print str(score).center(8) + "|" +\
      str(sum(scores)).center(7)+"|"
        
    # footer
    # '---------'
    print "'"+"-"*((maxlen) + (self.hand*8)+9)+"'"
  def solve(self, solution):
    ''' 
    *** solution should be a string where each card that was delt was used once
    *** and only once to equal the objective card.
    *** 
    *** Cards: 1, 3, 7, 1 8 = 1
    *** ((7 + ( 3 - 1))/1) - 8
    '''
    pass

  def print_cards(self):
    print " Cards: ",",".join([str(x) for x in self.cards])


if __name__ == "__main__":
  p = ["Fred","JoeBob","LongAssName","bo"]
  k = kryptobot(p)
  k.print_cards()
  k.print_scores()

