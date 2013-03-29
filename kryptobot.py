# twisted imports
from twisted.words.protocols import irc
from twisted.internet import reactor, protocol, ssl
 
# system imports
import threading
import functools
import time, sys, unicodedata
import krypto

class CountdownTimer(threading.Thread):
    def __init__(self,bot,channel,user,count_down):
      threading.Thread.__init__(self)
      self.event = threading.Event()
      self.count_down = count_down
      self.bot = bot
      self.channel = channel
      self.user = user

    def run(self):
      while self.count_down > 0 and not self.event.is_set():
        if self.count_down % 30 == 0:
          self.bot.msg(self.channel,self.user+ " you have " + str(self.count_down) + " seconds left")
        self.count_down -= 1
        self.event.wait(1)

      if not self.event.is_set():
      # The user did not put in a guess within the time limit
        self.bot.msg(self.channel,"Sorry " + self.user+ ", time ran out!")
        self.bot.guess(self.user,self.channel,"0")

    def stop(self):
      self.event.set()

class KryptoBot(irc.IRCClient):
    nickname = 'kryptobot' # nickname
    password = '' # server pass
    def __init__(self):

      self.krypto_game = None # curret kypto game
      self.timer = None
      self.guesser = None
      self.commands = {'help':[self.print_help,'Displays the list of commands'],\
                 'new':[self.start_new,'Initializes a new krypto game'],\
                 'join':[self.join_game,'Join the current kyrpto game.'],\
                 'start':[self.start_game,'After all players have joined, starts the krypto game.'],\
                 'end':[self.end_game,'Terminate the current krypto game'],\
                 'scores':[self.print_scores,'Show scores!'],\
                 'quick':[self.start_quick,'Will just do a quick game of krypto. \n\
                          No scoring will be done. \n\
                          Will not wait for players to join game.\n\
                          Will just display a single hand.'],\
                 'krypto':[self.start_timer,'During game play, it ends the current hand. The player who\
                          typed krypto has 1 minute to input a response.'],\
                 'guess':[self.guess,'if you typed in krypto, this will allow you to type in your guess.'],\
                 'solve':[self.solve,'Displays one possible solution to the current hand.'],\
                 'cards':[self.print_cards,'Displays the current set of cards again.']}
    def __get__(self, obj, objtype):
       """Support instance methods."""
       return functools.partial(self.__call__, obj)

    def connectionMade(self):
        irc.IRCClient.connectionMade(self)
        print "connectionMade"
 
    def connectionLost(self, reason):
        irc.IRCClient.connectionLost(self, reason)

    # callbacks for events
    def signedOn(self):
        """Called when bot has succesfully signed on to server."""
        self.join(self.factory.channel)
        print "joined server"
 
    def joined(self, channel):
        """This will get called when the bot joins the channel."""
        print "joined channel",channel
 
    def privmsg(self, user, channel, msg):
        """This will get called when the bot receives a message."""
        
        # Check to see if they're sending me a private message
        if channel == self.nickname:
            msg = "It isn't nice to whisper!  Play nice with the group."
            print msg
            self.msg(user, msg)
            return
        user = user.split("!")[0]
        # Otherwise check to see if it is a message directed at me
        if msg.startswith(self.nickname + ":") or msg.startswith(":"):
            func,args = self.decipher_cmd(channel,user,msg.split(":")[1].strip()) 
            if func != None:
              func(user,channel,args)
            return

    def decipher_cmd(self,channel,user,command):
      command = command.split()
      args = "".join(command[1:])
      command = command[0]
      print command,"-",args
      if command not in self.commands.keys():
        error = "'" + command + "'" + " is not a valid command"
        self.print_help(user,channel,error)
        return None,None
      func = self.commands[command][0]
      return func,args


    def print_help(self,user,channel,error=""):
       msg = error + "\n"
       msg += "Commands " + str(self.commands.keys())
#       msg += "Commands - Description\n"
#       msg += "=======   ===========\n"
#       for k,v in self.commands.iteritems():
#         print k,v[1]
#         msg += str(k).center(7) + " - " + str(v[1]) +"\n"
       self.msg(channel ,msg)

    def start_new(self,user,channel,arg):
      print "start new called"
      if self.krypto_game != None:
        self.msg(channel,"Please end current game before starting a new one.");
        return
      self.krypto_game = krypto.krypto([user])
      self.msg(channel,"New game started. You've been automatically added to the game. Waiting for others to join using the 'join' command. Issue the 'start' command once all the players have joined.");

    def join_game(self,user,channel,arg):
      print "join_game called"
      if self.krypto_game == None:
        self.msg(channel,"Please start a game before joining one.");
        return
      if self.krypto_game.join_game(user):
        self.msg(channel,user+" has been added to the game.");
      else:
        self.msg(channel,"Not joined to game.");

    def leave_game(self,user,channel,arg):
      print "leave_game called"
      if self.krypto_game == None:
        self.msg(channel,"Can't leave a game that hasn't started.");
        return
      if self.krypto_game.leave_game(user):
        self.msg(channel,user,"has been removed from the game.");
      else:
        self.msg(channel,"Sorry, the game has already started.");


    def start_game(self,user,channel,arg):
      print "start_game called"
      if self.krypto_game == None:
        self.msg(channel,"Please create a new game bofore starting it.");
        return

      if self.krypto_game.start_game():
        for p in self.krypto_game.players:
          self.msg(channel,p+": New Kryto Game Starting!\n")
        self.print_cards(user,channel,arg)
      else: 
        self.msg(channel,"You cannot start a game that is already in progress.")

    def print_scores(self,user,channel,arg):
      print "print_score called"
      if self.krypto_game != None and self.krypto_game.scored():
        print self.krypto_game.hand
        self.msg(channel,str(self.krypto_game))
        print self.krypto_game
      else: 
        self.msg(channel,"Game not scored")


    def end_game(self,user,channel,arg):
      print "end_game called"
      if self.krypto_game != None:
        if self.krypto_game.scored():
          self.msg(channel,str(self.krypto_game))
          print self.krypto_game
      self.krypto_game = None
      
    def start_quick(self,user,channel,arg):
      print "start_quick called"
      if self.krypto_game != None:
        self.msg(channel,"Please end current game before staring a new one.");
        return
      self.msg(channel,"New quick game started!");
      self.krypto_game = krypto.krypto([user],False)
      self.krypto_game.deal_next()
      self.print_cards(user,channel,arg)

    def start_timer(self,user,channel,arg):
      print "start_timer called"
      if self.krypto_game == None:
        self.msg(channel,user + ": please start a game before attempting to say 'Krypto!'")
        return
 
      if self.guesser != None:
        self.msg(channel,user + ", sorry someone else already said krypto.")
        return

      self.guesser = user
      self.timer = CountdownTimer(self,channel,user,3 * 60)
      self.timer.start()

    def guess(self,user,channel,arg):
      print "guess called"
      if self.krypto_game == None:
        self.msg(channel,user + ": please start a game before attempting a guess")
        return

      print self.guesser,user
      if not self.ok_to_guess(channel,user):
        return

      correct,solution = self.krypto_game.check_solution(user,arg)
      print correct,solution
      if correct:
        self.msg(channel,"Nice job, " + user + "! You got the answer correct!")
      else:
        self.msg(channel,"Nice try, " + user + ", but that was not a correct solution. Your solution evaluates to:"+str(solution))
        if self.krypto_game.scored():
          self.msg(channel,"One solution was " + str(self.krypto_game.solver()))

      if self.krypto_game.game_over():
        self.msg(channel,"Game Over!")
        self.msg(channel,str(self.krypto_game))
        self.krypto_game = None
      elif correct or self.krypto_game.scored():
        self.krypto_game.deal_next()
        self.print_cards(user,channel,arg)
         
    def ok_to_guess(self,channel,user):
      if self.guesser == user:
        if self.timer != None:
          self.timer.stop()
          self.timer = None
          self.guesser = None
          print "resetting timer and guesser",self.guesser
        return True
      elif self.guesser != None:
        self.msg(channel,user + ", sorry you can't guess/solve until " + self.guesser + " guesses.")
        return False
      else:
        self.msg(channel,user + ", sorry you can't guess/solve until you declare krypto")
        return False

      
    def solve(self,user,channel,arg):
      print "solve called"
      if self.krypto_game == None:
        self.msg(channel,user + ": please start a game before attempting to solve")
        return

      if not self.ok_to_guess(channel,user):
        return
      
      self.msg(channel,str(self.krypto_game.solver()))
      self.krypto_game.score_hand(user,False)
      self.krypto_game.deal_next()
      self.print_cards(user,channel,arg)

    def print_cards(self,user,channel,arg):
      print "print_cards called"
      if self.krypto_game == None:
        self.msg(channel,user + ": please start a game before attempting to print cards")
        return
      self.msg(channel,self.krypto_game.print_cards())
      

    def alterCollidedNick(self, nickname):
        return nickname+'_'
 
    def action(self, user, channel, msg):
        """This will get called when the bot sees someone do an action."""
        pass
 
    # irc callbacks
    def irc_NICK(self, prefix, params):
        """Called when an IRC user changes their nickname."""
        pass
 
 
class KryptoBotFactory(protocol.ClientFactory):
    """A factory for KryptoBots.
 
    A new protocol instance will be created each time we connect to the server.
    """
    protocol = KryptoBot
 
    def __init__(self):
        self.channel = '#SuperBestFriendsHappyFunClub' #channel
 
    def clientConnectionLost(self, connector, reason):
        """If we get disconnected, reconnect to server."""
        connector.connect()
 
    def clientConnectionFailed(self, connector, reason):
        print "connection failed:", reason
        reactor.stop()
 
 
if __name__ == '__main__':
    
    # create factory protocol and application
    f = KryptoBotFactory()
 
    # connect factory to this host and port
    hostname = 'gibson.freenode.net' # irc-server-hostname
    port = 7000 #port, ssl port
    reactor.connectSSL(hostname, port, f, ssl.ClientContextFactory())
 
    # run bot
    reactor.run()
 
