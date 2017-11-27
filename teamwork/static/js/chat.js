$(function () {
            //Parses messages for the @ sign and makes them a link
            function parseAtSign(msg){
                var split_message = msg.split(" ");
                var finished_message = "";
                for(var i = 0; i < split_message.length; i++){
                    if(split_message[i].charAt(0) === "@"){
                        finished_message = finished_message.concat(
                            "<a href=\"{% url 'find_user_profile' " +
                            split_message[i] +
                            " %}\">" +
                            split_message[i] +
                            " </a>");
                    }
                    else{
                        finished_message = finished_message.concat(split_message[i]+" ");
                    }
                }
                return finished_message;
            }
            // Correctly decide between ws:// and wss://
            var ws_path = "/chat/stream/";
            console.log("Connecting to " + ws_path);

            var webSocketBridge = new channels.WebSocketBridge();
            webSocketBridge.connect(ws_path);

            console.log("Current user is: "+current_user);
            //When the websocket receives a payload it needs to decide what type it is
            //then handle it.
            webSocketBridge.listen(function(data) {
                // Decode the JSON
                console.log("Got websocket message", data);
                // Handle errors
                if (data.error) {
                    alert(data.error);
                    return;
                }
                // When you join this creates the room
                if (data.join) {
                    console.log("Joining room " + data.join);
                    var roomdiv = $(
                            "<div class=\"box box-success direct-chat direct-chat-success\">" +
                              "<div class=\"box-header with-border\">" +
                                "<h3 class=\"box-title\">"+data.title+"</h3>" +
                                "<div class=\"box-tools pull-right\">" +
                                  "<button class=\"btn btn-box-tool\" data-widget=\"collapse\"><i class=\"fa fa-minus\"></i></button>" +
                                "</div>" +
                              "</div>" +
                              "<div class=\"box-body\">" +
                                "<!-- Conversations are loaded here -->" +
                                "<div id= \"msg_box\" class=\"direct-chat-messages\">" +

                                /*
                                  "<!-- Message. Default to the left -->" +
                                    "<div id= \"one_msg_left\" class=\"direct-chat-msg\">" +
                                      "<div id=\"msg_info_left\" class=\"direct-chat-info clearfix\">" +
                                        // This is where message info (from people other than current_user)
                                        // such as name and time will appear
                                        //"<span class=\"direct-chat-name pull-left\">"+data.username+"</span>" +
                                        //"<span class=\"direct-chat-timestamp pull-right\">"+data.date+"</span>" +
                                      "</div>" +
                                      "<!-- /.direct-chat-info -->" +
                                      "<div id=\"msg_text_left\" class=\"direct-chat-text\">" +
                                        // This is where Message text will appear (except current_user, see below)
                                      "</div>" +
                                      "<!-- /.direct-chat-text -->" +
                                    "</div>" +
                                    "<!-- /.direct-chat-msg -->" +
                                    //
                                    "<!-- Message to the right -->" +
                                    "<div id= \"one_msg_right\" class=\"direct-chat-msg right\">" +
                                      "<div id= \"msg_info_right\" class=\"direct-chat-info clearfix\">" +
                                        // The current_user's info will show up below.
                                        //"<span class=\"direct-chat-name pull-right\">INSERT_USER_2_HERE</span>" +
                                        //"<span class=\"direct-chat-timestamp pull-left\">INSERT_TIME_2_HERE</span>" +
                                      "</div>" +
                                      "<!-- /.direct-chat-info -->" +
                                      "<div id=\"msg_text_right\" class=\"direct-chat-text\">" +
                                        // current_user's message text will appear here.
                                      "</div>" +
                                      "<!-- /.direct-chat-text -->" +
                                    "</div>" +
                                    "<!-- /.direct-chat-msg -->" +
                                    //
                                  "</div>" +
                                  "<!--/.direct-chat-messages-->" +
                                  */
                                "</div>" +
                                "<!-- /.box-body -->" +
                                "<div class=\"box-footer\">" +
                                  "<div class=\"input-group\">" +
                                    "<div class='messages'></div>" +
                                      "<form>" 
				   
    				  
                                      "<input type=\"text\" name=\"message\" placeholder=\"Type Message ...\" class=\"form-control\">" +
                                      //"<span class=\"input-group-btn\">" +
				      
				      
                                        "<button type=\"button\" class=\"btn btn-success btn-flat\" onclick=\"submit\">Send</button>" +
                                      //"</span>" +
				      
				  
                                      "</form>"+
                                  "</div>" +
                                "</div>" +
                                "<!-- /.box-footer-->" +
                              "</div>" +
                              "<!--/.direct-chat -->" +

                            "<div class='room' id='room-" + data.join + "'>" +
                              "<div class='messages'></div>" +
                              //"<form>Your message<input><button>Send</button></form>" +
                            "</div>"
                    );
                    // Hook up send button to send a message
                    roomdiv.find("form").on("submit", function () {
                        webSocketBridge.send({
                            "command": "send",
                            "room": data.join,
                            "message": roomdiv.find("input").val()
                        });
                        roomdiv.find("input").val("");
                        return false;
                    });
                    $("#chats").append(roomdiv);
                 //Removes the room when click the room link again
                } else if (data.leave) {
                    console.log("Leaving room " + data.leave);
                    $("#room-" + data.leave).remove();
                    // Handle getting a message
                } else if (data.message) {
                    var msgdiv = $("#room-" + data.chatroom + " .messages");
                    user_message = parseAtSign(data.message);
                    one_msg = document.getElementById("msg_box");
                    if(current_user === data.message.username){
                        //one_msg = document.getElementById("one_msg_right");
                        one_msg.innerHTML += "<div id= \"one_msg_right\" class=\"direct-chat-msg right\">" +
                                            "<div id=\"msg_info_right\" class=\"direct-chat-info clearfix\">" +
                                            "<span class=\"direct-chat-name pull-left\">"+data.username+"</span>" +
                                            "<span class=\"direct-chat-timestamp pull-right\">"+data.date+"</span>" +
                                            "</div>" +
                                            "<div id=\"msg_text_right\" class=\"direct-chat-text\">" +
                                            user_message +
                                            "</div>"+
                                            "</div>";
                    }
                    else{
                        //one_msg = document.getElementById("one_msg_left");
                        one_msg.innerHTML += "<div id= \"one_msg_left\" class=\"direct-chat-msg\">" +
                                            "<div id=\"msg_info_left\" class=\"direct-chat-info clearfix\">" +
                                            "<span class=\"direct-chat-name pull-left\">"+data.username+"</span>" +
                                            "<span class=\"direct-chat-timestamp pull-right\">"+data.date+"</span>" +
                                            "</div>" +
                                            "<div id=\"msg_text_left\" class=\"direct-chat-text\">" +
                                            user_message +
                                            "</div>"+
                                            "</div>";
                    }
                    var msg_box_div = document.getElementById("msg_box");
                    msg_box_div.scrollTop = msg_box_div.scrollHeight;
                    //msgdiv.scrollTop(msgdiv.prop("scrollHeight"));
                }else if (data.messages) {
                    for (var i = 0; i < data.messages.length; i++){
                        var msgdiv = $("#room-" + data.messages[i].chatroom + " .messages");
                        user_message = parseAtSign(data.messages[i].message);
                        one_msg = document.getElementById("msg_box");
                        if(current_user === data.messages[i].username){
                            //one_msg = document.getElementById("one_msg_right");
                            one_msg.innerHTML += "<div id= \"one_msg_right\" class=\"direct-chat-msg right\">" +
                                                "<div id=\"msg_info_right\" class=\"direct-chat-info clearfix\">" +
                                                // This is where message info like name and time will appear
                                                "<span class=\"direct-chat-name pull-left\">"+data.messages[i].username+"</span>" +
                                                "<span class=\"direct-chat-timestamp pull-right\">"+data.messages[i].date+"</span>" +
                                                "</div>" +
                                                "<div id=\"msg_text_right\" class=\"direct-chat-text\">" +
                                                user_message +
                                                "</div>"+
                                                "</div>";
                        }
                        else{
                            //one_msg = document.getElementById("one_msg_left");
                            one_msg.innerHTML += "<div id= \"one_msg_left\" class=\"direct-chat-msg\">" +
                                                "<div id=\"msg_info_left\" class=\"direct-chat-info clearfix\">" +
                                                // This is where message info like name and time will appear
                                                "<span class=\"direct-chat-name pull-left\">"+data.messages[i].username+"</span>" +
                                                "<span class=\"direct-chat-timestamp pull-right\">"+data.messages[i].date+"</span>" +
                                                "</div>" +
                                                "<div id=\"msg_text_left\" class=\"direct-chat-text\">" +
                                                user_message +
                                                "</div>"+
                                                "</div>";
                        }
                    }
                    var msg_box_div = document.getElementById("msg_box");
                    msg_box_div.scrollTop = msg_box_div.scrollHeight;
                    //msgdiv.scrollTop(msgdiv.prop("scrollHeight"));
                } else {
                    console.log("Cannot handle message!");
                }
            });

            // Says if we joined a room or not by if there's a div for it
            inRoom = function (roomId) {
                return $("#room-" + roomId).length > 0;
            };

            // Helpful debugging
            webSocketBridge.socket.onopen = function () {
                console.log("Connected to chat socket");
                roomId = $("li.room-link").attr("data-room-id");
                // Initial message payload sent when you join a room
                $("li.room-link").addClass("joined");
                webSocketBridge.send({
                    "command": "join",
                    "room": roomId
                });
            };
            webSocketBridge.socket.onclose = function () {
                console.log("Disconnected from chat socket");
                roomId = $("li.room-link").attr("data-room-id");
                // Payload sent when you leave a room
                $("li.room-link").removeClass("joined");
                webSocketBridge.send({
                    "command": "leave",
                    "room": roomId
                });
            }
        });
