$(function () {
			//thank you stack overflow
			//https://gist.github.com/dperini/729294
			//idk wtf cause long regex
			function validURL(str) {
				var pattern = new RegExp(
  "^" +
    // protocol identifier
    "(?:(?:https?|ftp)://)" +
    // user:pass authentication
    "(?:\\S+(?::\\S*)?@)?" +
    "(?:" +
      // IP address exclusion
      // private & local networks
      "(?!(?:10|127)(?:\\.\\d{1,3}){3})" +
      "(?!(?:169\\.254|192\\.168)(?:\\.\\d{1,3}){2})" +
      "(?!172\\.(?:1[6-9]|2\\d|3[0-1])(?:\\.\\d{1,3}){2})" +
      // IP address dotted notation octets
      // excludes loopback network 0.0.0.0
      // excludes reserved space >= 224.0.0.0
      // excludes network & broacast addresses
      // (first & last IP address of each class)
      "(?:[1-9]\\d?|1\\d\\d|2[01]\\d|22[0-3])" +
      "(?:\\.(?:1?\\d{1,2}|2[0-4]\\d|25[0-5])){2}" +
      "(?:\\.(?:[1-9]\\d?|1\\d\\d|2[0-4]\\d|25[0-4]))" +
    "|" +
      // host name
      "(?:(?:[a-z\\u00a1-\\uffff0-9]-*)*[a-z\\u00a1-\\uffff0-9]+)" +
      // domain name
      "(?:\\.(?:[a-z\\u00a1-\\uffff0-9]-*)*[a-z\\u00a1-\\uffff0-9]+)*" +
      // TLD identifier
      "(?:\\.(?:[a-z\\u00a1-\\uffff]{2,}))" +
      // TLD may end with dot
      "\\.?" +
    ")" +
    // port number
    "(?::\\d{2,5})?" +
    // resource path
    "(?:[/?#]\\S*)?" +
  "$", "i"
);
				return pattern.test(str);
			}
            //Parses messages for the @ sign and makes them a link
            function parseAtSign(msg){
                var split_message = msg.split(" ");
                var finished_message = "";
                for(var i = 0; i < split_message.length; i++){
                    if(split_message[i].charAt(0) === "@"){
                        //This just works for some reason as a url
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

            function parseImgLinks(msg){
                var split_message = msg.split(" ");
                var finished_message = "";
                for(var i = 0; i < split_message.length; i++){
					if(validURL(split_message[i])){
						if(split_message[i].endsWith(".png")||
							split_message[i].endsWith(".gif")||
							split_message[i].endsWith(".jpg")||
							split_message[i].endsWith(".bmp")){
							finished_message = finished_message.concat(
								"<img width=\"300\" height=\"300\" src=\"" +
								split_message[i] +
								"\">" +
								" </img>");
						}else if(split_message[i].endsWith(".gifv")){
							finished_message = finished_message.concat(
								"<video preload=\"auto\" autoplay=\"autoplay\" loop=\"loop\" width=\"300\" height=\"300\">" +
								"<source src=\""+
								split_message[i].replace(".gifv",".mp4")+
								"\" type=\"video/mp4\"></source>" +
								" </video>");
						}else if(split_message[i].endsWith(".mp4")){
							finished_message = finished_message.concat(
								"<video preload=\"auto\" autoplay=\"autoplay\" loop=\"loop\" width=\"300\" height=\"300\">" +
								"<source src=\""+
								split_message[i]+
								"\" type=\"video/mp4\"></source>" +
								" </video>");
						}else if(split_message[i].endsWith(".webm")){
							finished_message = finished_message.concat(
								"<video preload=\"auto\" autoplay=\"autoplay\" loop=\"loop\" width=\"300\" height=\"300\">" +
								"<source src=\""+
								split_message[i]+
								"\" type=\"video/webm\"></source>" +
								" </video>");
						}else{
							finished_message = finished_message.concat(split_message[i]+" ");
						}
                    }
                    else{
                        finished_message = finished_message.concat(split_message[i]+" ");
                    }
                }
                return finished_message;
            }
			//text to speach function, any options are to be put in here
			function text_to_speach(msg){
				var spokenWordObject = new SpeechSynthesisUtterance(msg);
				window.speechSynthesis.speak(spokenWordObject);
			}
			function websocket_get_rooms(){
				
                webSocketBridge.send({
                    "command": "join_many",
                    "rooms": array_of_rooms
                    });
			}
			$("#reinit_rooms").click(websocket_get_rooms);
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
                if (data.rooms){
                    console.log("Joining rooms");
                    for(var roomNum = 0;roomNum<data.rooms.length;roomNum++){
                        var leaveUrl = leaveURLBase.replace(/9234523426/, data.rooms[roomNum].join.toString());
                        var inviteUrl = inviteURLBase.replace(/9234523426/, data.rooms[roomNum].join.toString());
                        var roomdiv = $(
                            "<div class=\"box box-success direct-chat direct-chat-success\">" +
                              "<div class=\"box-header with-border\">" +
                                "<h3 class=\"box-title\">"+data.rooms[roomNum].title+"</h3>" +
                                "<div class=\"box-tools pull-right\">" +
                                  "<button class=\"btn btn-box-tool\" data-widget=\"collapse\"><i class=\"fa fa-minus\"></i></button>" +
                                "</div>" +
                              "</div>" +
                              "<div class=\"box-body\">" +
                                "<button id=\"load_more_messages\" class=\"btn btn-success btn-flat\" data-MSGnumber=10 data-room-number="+data.rooms[roomNum].join+">Load more messages</button>"+
                                "<!-- Conversations are loaded here -->" +
                                "<div id= \"msg_box"+data.rooms[roomNum].join+"\" class=\"direct-chat-messages\">" +

                                // Each individual message is loaded into here

                                "</div>" +
                                "<!-- /.box-body -->" +
                                "<div class=\"box-footer\">" +
                                  "<div class=\"input-group\">" +
                                    "<div class='messages'></div>" +
                                      "<form id=\"send_msg\">" +
                                      "<input size=\"100\" type=\"text\" name=\"message\" data-room-number="+data.rooms[roomNum].join+" placeholder=\"Type Message ...\" class=\"form-control\">"  + 
                                      "<span class=\"input-group-btn\">" +
                                        "<button type=\"submit\" class=\"btn btn-success btn-flat\" onclick=\"submit\">Send</button>" +
                                      "</span>" +
                                      "</form>"+
                                  "</div>" +
                                "</div>" +
                                "<!-- /.box-footer-->" +
                                "<a href=\""+inviteUrl+"\">"+
                                "<button class=\"btn btn-primary\" type=\"button\">"+
                                "Invite Users"+
                                "</button>"+
                                "</a>"+
                                "<a href=\""+leaveUrl+"\">"+
                                "<button class=\"btn btn-danger\" type=\"button\">"+
                                "Leave Chatroom"+
                                "</button>"+
                                "</a>"+
                              "</div>" +
                              "<!--/.direct-chat -->"
                        );
						if($("#msg_box"+data.rooms[roomNum].join).length==0){
							$("#tab_"+data.rooms[roomNum].join).append(roomdiv);
						}
                    }
                    //hook up all thesend buttons
                    $("form").submit( function(e) {
                        e.preventDefault();
                        webSocketBridge.send({
                            "command": "send",
                            "room": $(this).find("input").data().roomNumber,
                            "message": $(this).find("input").val()
                        });
                        $(this).find("input").val("");
                    });
                    $('button[id="load_more_messages"]').click(function(){
                        console.log("getting more messages")
                        webSocketBridge.send({
                            "command": "get_old",
                            "room": $(this).data().roomNumber,
                            "number": $(this).data().msgnumber
                        });
                        $(this).data().msgnumber+=10;
                    })
					

                }
                 //Removes the room when click the room link again
                if (data.leave) {
                    console.log("Leaving room " + data.leave);
                    $("#room-" + data.leave).remove();
                    // Handle getting a message
                } else if (data.message) {
                    //var msgdiv = $("#room-" + data.chatroom + " .messages");
                    user_message = parseImgLinks(parseAtSign(data.message));
                    one_msg = document.getElementById("msg_box"+data.chatroom);
                    one_msg.innerHTML += "<!-- chat item -->"+
                                        "<div class=\"item\">"+
                                        "<p class=\"message\">"+
                                        "<img src=\"https://www.gravatar.com/avatar/"+data.gravitar+"\" class=\"img-circle\" alt=\"User Image\" height=\"42\" width=\"42\" style='float: left;'>"+
                                        "&nbsp&nbsp&nbsp"+
                                        "<a href=\"#\" class=\"name\">"+
                                        "<small class=\"text-muted pull-right\"><i class=\"fa fa-clock-o\"></i>"+data.date+"</small>"+
                                        data.username+
                                        "</a><br /><div class=\"text\">&nbsp&nbsp&nbsp"+
                                        user_message +
                                        "</div></p><br />"+
                                        "</div>"+
                                        "<!-- /.item -->";
                    /*if(current_user === data.message.username){
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
                    }*/
                    var msg_box_div = document.getElementById("msg_box"+data.chatroom);
                    msg_box_div.scrollTop = msg_box_div.scrollHeight;
					
					$("div.item").click(function(){
						console.log($(this).find(".text").html())
						text_to_speach($(this).find(".text").html().replace("&nbsp;&nbsp;&nbsp;",""));
					})
                    //msgdiv.scrollTop(msgdiv.prop("scrollHeight"));
                }else if (data.oldmessages) {
                    var one_msg = document.getElementById("msg_box"+data.oldmessages[0].chatroom);
                    var initial_msgs = one_msg.innerHTML;
                    one_msg.innerHTML = "";
                    for (var i = data.oldmessages.length-1; i >= 0; i--){
                        //var msgdiv = $("#room-" + data.oldmessages[i].chatroom + " .messages");
                        var user_message = parseImgLinks(parseAtSign(data.oldmessages[i].message));
                        one_msg.innerHTML += "<!-- chat item -->"+
                                            "<div class=\"item\">"+
                                            "<p class=\"message\">"+
                                            "<img src=\"https://www.gravatar.com/avatar/"+data.oldmessages[i].gravitar+"\" class=\"img-circle\" alt=\"User Image\" height=\"42\" width=\"42\" style='float: left;'>"+
                                            "&nbsp&nbsp&nbsp"+
                                            "<a href=\"#\" class=\"name\">"+
                                            "<small class=\"text-muted pull-right\"><i class=\"fa fa-clock-o\"></i>"+data.oldmessages[i].date+"</small>"+
                                            data.oldmessages[i].username+
                                            "</a><br /><div class=\"text\">&nbsp&nbsp&nbsp"+
                                            user_message +
                                            "</div></p><br />"+
                                            "</div>"+
                                            "<!-- /.item -->";
                    }
                    one_msg.innerHTML += initial_msgs;
					
					$("div.item").click(function(){
						console.log($(this).find(".text").html())
						text_to_speach($(this).find(".text").html().replace("&nbsp;&nbsp;&nbsp;",""));
					})

                        /*if(current_user == data.oldmessages[i].username){
                            //one_msg = document.getElementById("one_msg_right");
                            one_msg.innerHTML = "<div id= \"one_msg_right\" class=\"direct-chat-msg right\">" +
                                                "<div id=\"msg_info_right\" class=\"direct-chat-info clearfix\">" +
                                                // This is where message info like name and time will appear
                                                "<span class=\"direct-chat-name pull-left\">"+data.oldmessages[i].username+"</span>" +
                                                "<span class=\"direct-chat-timestamp pull-right\">"+data.oldmessages[i].date+"</span>" +
                                                "</div>" +
                                                "<div id=\"msg_text_right\" class=\"direct-chat-text\">" +
                                                user_message +
                                                "</div>"+
                                                "</div>"+
                                                one_msg.innerHTML;
                        }
                        else{
                            //one_msg = document.getElementById("one_msg_left");
                            one_msg.innerHTML = "<div id= \"one_msg_left\" class=\"direct-chat-msg\">" +
                                                "<div id=\"msg_info_left\" class=\"direct-chat-info clearfix\">" +
                                                // This is where message info like name and time will appear
                                                "<span class=\"direct-chat-name pull-left\">"+data.oldmessages[i].username+"</span>" +
                                                "<span class=\"direct-chat-timestamp pull-right\">"+data.oldmessages[i].date+"</span>" +
                                                "</div>" +
                                                "<div id=\"msg_text_left\" class=\"direct-chat-text\">" +
                                                user_message +
                                                "</div>"+
                                                "</div>"+
                                                one_msg.innerHTML;
                        }*/
                    //msgdiv.scrollTop(msgdiv.prop("scrollHeight"));
                }else if (data.messages) {
                    for (var i = 0; i < data.messages.length; i++){
                        //var msgdiv = $("#room-" + data.messages[i].chatroom + " .messages");
                        user_message =parseImgLinks(parseAtSign(data.messages[i].message));
                        one_msg = document.getElementById("msg_box"+data.messages[i].chatroom);

                        one_msg.innerHTML += "<!-- chat item -->"+
                                            "<div class=\"item\">"+
                                            "<p class=\"message\">"+
                                            "<img src=\"https://www.gravatar.com/avatar/"+data.messages[i].gravitar+"\" class=\"img-circle\" alt=\"User Image\" height=\"42\" width=\"42\" style='float: left;'>"+
                                            "&nbsp&nbsp&nbsp"+
                                            "<a href=\"#\" class=\"name\">"+
                                            "<small class=\"text-muted pull-right\"><i class=\"fa fa-clock-o\"></i>"+data.messages[i].date+"</small>"+
                                            data.messages[i].username+
                                            "</a><br /><div class=\"text\">&nbsp&nbsp&nbsp "+
                                            user_message +
                                            "</div></p><br />"+
                                            "</div>"+
                                            "<!-- /.item -->";
                        var msg_box_div = document.getElementById("msg_box"+data.messages[i].chatroom);
                        msg_box_div.scrollTop = msg_box_div.scrollHeight;
                    }
					$("div.item").click(function(){
						console.log($(this).find(".text").html())
						text_to_speach($(this).find(".text").html().replace("&nbsp;&nbsp;&nbsp;",""));
					})
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
                //array_of_rooms.forEach(function(element) {
                //	webSocketBridge.send({
                //    "command": "join",
                //    "room": element
                //	});
                //});
				websocket_get_rooms()

            };
            webSocketBridge.socket.onclose = function () {
                console.log("Disconnected from chat socket");
                array_of_rooms.forEach(function(element) {
                    webSocketBridge.send({
                    "command": "leave",
                    "room": element
                    });
                });
            }
        });
