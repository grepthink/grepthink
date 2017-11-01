GrepThink
========

[![Build Status](https://travis-ci.org/grepthink/grepthink.svg?branch=master)](https://travis-ci.org/grepthink/grepthink)
[![Coverage Status](https://coveralls.io/repos/github/grepthink/grepthink/badge.svg?branch=production)](https://coveralls.io/github/grepthink/grepthink?branch=production)

Build better teams, one match at a time!<br /><br />
Our Team:<br />
Sean Gordon<br />
Hugh Feng<br />
Trevor Ching<br />
Anjali Kanthilal<br />
Ali Alkaheli<br />
<br />
Fall17 Fork Changelog:<br />
10-18-17 4:27pm - Sean's change<br />
10-19-17 5:24pm - Hugh's change<br />
10-20-17 12:50pm - Sean added Release plan, Sprint 1 plan, and intro slides to ./docs/fall17<br />
10-20-17 1:35pm - Sean Synced fork with GrepThink upstream<br />
10-20-17 2:20pm - Sean added chat app under ./teamwork/apps and added Sprint 1 Report under ./docs/fall17<br />
10-23-17 10:35am - Sean added Sprint 2 plan and updated Sprint 1 Report in ./docs/fall17<br />
10-26-17 10:50pm - Trevor Messages should be routed to consumers and sent into a chat room along with basic error checking. Also made a basic chat html page
that only lists the chat rooms created. Chat rooms can be created through the admin page and users can be added into the room. Have not tested the actual chat
because I am unable to link into a chat room or create a chat room via a link when listing the chat rooms. So the message system is not tested yet, but the website
still loads.<br />
10-27-17 1:54pm - Anjali added chat side bar to _main_sidebar.html so it connects to chat.html<br />
10-27-17 2:32pm - Trevor, Basic messaging functions work, messages can be received from users in the same room.
Chat room still needs to be created and implemented into the grepthink base.html file.<br />
10-24-17 ->10-29-17 models are implemented, small fixes in various places, teying to get testing working. Please understand what you read, don't just copy<br />
11-1-17 - Sean: Added sub urls from /chat (for ex. /chat/room1) and now the chatroom auto loads upon entering those sub-urls.<br />
