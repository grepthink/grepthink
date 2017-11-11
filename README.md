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
11-1-17 12:30pm - Sean: Added sub urls from /chat (for ex. /chat/room1) and now the chatroom auto loads upon entering those sub-urls. Breadcrumbs are added for both view_chats and view_one_chat.<br />
11-2-17 8:20pm - Sean: Deleted unneeded code in chat.html, set proper leave in one_chat.html for a websocket disconnect, deleted unneeded copy file "chat - Copy.html". Working on user authenication next.<br />
11-3-17 12:37 - Hugh: get messages added, working much better.<br />
11-4-17 2:50pm - Trevor: Made projects and chat connected not by foreign key anymore. When a project is created a chat is created with it, when members are added to the project they are added to the
chat, and when someone is removed or leaves from the project they are removed from the chat. This should not interfere with current projects already in the datbase because it checks
for existing chats matching the project title name, which may cause other errors if a chat is created with the project name.......<br />
11-5-17 6:15pm - Sean: Added authentication to chat views. Only lists user's chatrooms in "/chat" (no longer all of them) and if someone tries to get get into a chat via url slug, checks if they are a member of the room.<br />
11-5-17 10:45pm - Sean: Added chat layout UI, loads adminlte template, & previous messages (scrolling isn't quite right yet). Newly sent messages also appear in the new chat box. Use the GREY button to send, working on GREEN, but it's not quite finished. Keeping the basic chat texts for now in case of bugs or for testing. Added Sprint 2 Report under docs/fall17.<br />
11-9-17 3:46pm - Trevor: Made chats connected to projects created with dash in the front. Need to make dashes not allowed in chat names when creating chat forms. Made the @ backend parsing assuming the frontend removes the @ sign. <br />
11-10-17 5:25pm - Sean: Added a "Creat Chatroom" on the "/chat" url. Takes you to a form where you can set an name and add users. After Submitting the form, takes you back to the "/chat" url.<br />
