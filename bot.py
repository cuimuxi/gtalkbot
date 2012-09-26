#!/usr/bin/python -u
#-*- coding:utf-8 -*-

import sys
import logging
import codecs

from pyxmpp.all import JID,Iq,Presence,Message,StreamError
from pyxmpp.jabber.client import JabberClient
from pyxmpp.interface import implements
from pyxmpp.interfaces import *
from pyxmpp.streamtls import TLSSettings
from settings import USER, PASSWORD
from cmd import run_cmd, send_all_msg, send_command
from db import add_member, del_member



class BotHandler(object):

    implements(IMessageHandlersProvider, IPresenceHandlersProvider)

    def __init__(self, client):
        """Just remember who created this."""
        self.client = client

    def get_message_handlers(self):
        return [
            ("normal", self.message),
            ]

    def get_presence_handlers(self):
        return [
            (None, self.presence),
            ("unavailable", self.presence),
            ("subscribe", self.presence_control),
            ("subscribed", self.presence_control),
            ("unsubscribe", self.presence_control),
            ("unsubscribed", self.presence_control),
            ]

    def message(self,stanza):
        body=stanza.get_body()
        subject=stanza.get_subject()
        t=stanza.get_type()
        print u'Message from %s received.' % (unicode(stanza.get_from(),)),
        if subject:
            print u'Subject: "%s".' % (subject,),
        if t:
            print u'Type: "%s".' % (t,)
        else:
            print u'Type: "normal".'
        if stanza.get_type()=="headline":
            # 'headline' messages should never be replied to
            return True
        if subject:
            subject=u"Re: "+subject
        if not body:
            print u'Body: "%s".' % (body,),
            return
        if body.startswith('$'):
            m = send_command(stanza, body)
        else:
            m = send_all_msg(stanza, body)
        print 'messge',m
        print 'message dir', dir(m)
        if isinstance(m, list):
            for i in m:
                print 'message to', i.get_to()
                print 'message type', i.get_type()
                print 'message body', i.get_body()
        else:
            print 'message to', m.get_to()
            print 'message body', m.get_body()
            print 'message type', m.get_type()


        return m



    def presence(self,stanza):
        msg=u"%s has become " % (stanza.get_from())
        t=stanza.get_type()
        if t=="unavailable":
            msg+=u"unavailable"
        else:
            msg+=u"available"
        show=stanza.get_show()
        if show:
            msg+=u"(%s)" % (show,)

        status=stanza.get_status()
        if status:
            msg+=u": "+status
        print msg

    def presence_control(self,stanza):
        msg=unicode(stanza.get_from())
        t=stanza.get_type()
        frm = stanza.get_from()
        if t=="subscribe":
            msg+=u" has requested presence subscription."
            body = "%s 加入群" % frm.node
            send_all_msg(stanza, body)  
            add_member(frm)
        elif t=="subscribed":
            msg+=u" has accepted our presence subscription request."
            add_member(frm)
        elif t=="unsubscribe":
            msg+=u" has canceled his subscription of our."
            body = "%s 离开群" % frm.node
            send_all_msg(stanza, body)
            del_member(frm)
        elif t=="unsubscribed":
            msg+=u" has canceled our subscription of his presence."
            del_member(frm)

        print msg

        return stanza.make_accept_response()


class VersionHandler(object):

    implements(IIqHandlersProvider, IFeaturesProvider)

    def __init__(self, client):
        self.client = client

    def get_features(self):
        return ["jabber:iq:version"]

    def get_iq_get_handlers(self):
        return [
            ("query", "jabber:iq:version", self.get_version),
            ]

    def get_iq_set_handlers(self):
        return []

    def get_version(self,iq):
        iq=iq.make_result_response()
        q=iq.new_query("jabber:iq:version")
        q.newTextChild(q.ns(),"name","Echo component")
        q.newTextChild(q.ns(),"version","1.0")
        return iq

class Client(JabberClient):

    def __init__(self, jid, password):
        if not jid.resource:
            jid=JID(jid.node, jid.domain, "bot")

            tls_settings = TLSSettings(require = True, verify_peer = False)

        JabberClient.__init__(self, jid, password, auth_methods=['sasl:PLAIN'],
                disco_name="Pythoner Club", disco_type="bot",
                tls_settings = tls_settings)

        # add the separate components
        self.interface_providers = [
            VersionHandler(self),
            BotHandler(self),
            ]

    def stream_state_changed(self,state,arg):
        print "*** State changed: %s %r ***" % (state,arg)

    def print_roster_item(self,item):
        if item.name:
            name=item.name
        else:
            name=u""
        print (u'%s "%s" subscription=%s groups=%s'
                % (unicode(item.jid), name, item.subscription,
                    u",".join(item.groups)) )

    def roster_updated(self,item=None):
        if not item:
            print u"My roster:"
            for item in self.roster.get_items():
                self.print_roster_item(item)
            return
        print u"Roster item updated:"
        self.print_roster_item(item)

encoding = "utf-8"
sys.stdout = codecs.getwriter(encoding)(sys.stdout, errors = "replace")
sys.stderr = codecs.getwriter(encoding)(sys.stderr, errors = "replace")


logger = logging.getLogger()
logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.INFO) # change to DEBUG for higher verbosity


print u"creating client..."

c=Client(JID(USER), PASSWORD)

print u"connecting..."
c.connect()

print u"looping..."
try:
    # Component class provides basic "main loop" for the applitation
    # Though, most applications would need to have their own loop and call
    # component.stream.loop_iter() from it whenever an event on
    # component.stream.fileno() occurs.
    c.loop(None)
except KeyboardInterrupt:
    print u"disconnecting..."
    c.disconnect()

print u"exiting..."
