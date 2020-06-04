/**
 * (C) Copyright IBM Corp. 2019, 2020.
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *      http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

require.undef('transcript');

define('transcript', ['d3'], function (d3) {
  debugger;

  function draw(container, config, data) {
    if (config["debugger"] === true) {
      debugger;
    }

    var _config = {}, _chart = {}, _data = null;

    // draw one conversation and append to container
    _chart.drawSelectedConversation = function() {
      var selectedConversation = this.data[this.selected];
      var conversationBody = this.conversationBody;
      conversationBody.empty();
      var chipsDiv = $('<div>').appendTo(conversationBody);
      // create chips for insights
      if ("insight_tags" in selectedConversation) {
        var tags = Object.keys(selectedConversation.insight_tags);
        for (var i = 0; i < tags.length; i++) {
          var tag = tags[i];
          var tagCount = selectedConversation.insight_tags[tag];
          $('<span>', { text: tag + " (" + tagCount + ")"}).addClass("botvis-chip").appendTo(chipsDiv);
        }
      }
      //   alert("found insights chips" + selectedConversation.insights_tags);
      var ul = $('<ul>').addClass("botvis-timeline").appendTo(conversationBody)
      //ul.empty();
      this.conversation_span.text(selectedConversation.conversation.id + " (" + (this.selected+1)  + " of " + this.data.length + ")" );
      //this.conversation_span.text(this.data[this.selected].conversation.id);
      selectedConversation.events.forEach(function(item) {
        var timeline_li = $('<li>').appendTo(ul);
        if (item.type == 'request')
          timeline_li.addClass("botvis-timeline-inverted");
        else if (item.type == 'internal')
          timeline_li.addClass("botvis-timeline-internal");
        var timeline_panel = $('<div>').addClass("botvis-timeline-panel").appendTo(timeline_li);
        if (("highlight" in item) && (item.highlight)) {
          timeline_panel.addClass("botvis-timeline-panel-highlighted")
        }
        var timeline_heading = $('<div>').addClass("botvis-timeline-heading").appendTo(timeline_panel);
        var timeline_body = $('<div>').addClass("botvis-timeline-body").appendTo(timeline_panel);
        var timeline_bot_props = $('<div>').addClass("botvis-timeline-botprops").appendTo(timeline_panel);
        if ('action' in item)
          var timeline_bodyaction = $('<p>', { text:"action" + item.action}).addClass("botvis-timeline-botprops-action").appendTo(timeline_bot_props);
        if ('channel' in item)
          var timeline_channel = $('<p>', { text:"channel: " + item.channel}).addClass("botvis-timeline-botprops-channel").appendTo(timeline_bot_props);
        if ('node_visited' in item)
          var timeline_body_nodesvisited = $('<p>', { text:item.node_visited}).addClass("botvis-timeline-botprops-nodevisited").appendTo(timeline_bot_props);   
        //  ['turn_label', 'nodes_visited_str', 'nodes_visited']
        if (_config.display_fields.includes("skill_name") && ('skill_name' in item))
          var timeline_skill = $('<p>', { text:"skill: " + item.skill_name}).addClass("botvis-timeline-botprops-skillname").appendTo(timeline_bot_props);   
        if (_config.display_fields.includes("turn_label") && ('turn_label' in item))
          var timeline_skill = $('<p>', { text:item.turn_label}).addClass("botvis-timeline-botprops-turnlabel").appendTo(timeline_bot_props);   
        if (_config.display_fields.includes("nodes_visited_str") && ('nodes_visited_str' in item))
          var timeline_skill = $('<p>', { text:"[" + item.nodes_visited_str.join(',') + "]"}).addClass("botvis-timeline-botprops-nodevisitedstr").appendTo(timeline_bot_props);   
        if (_config.display_fields.includes("nodes_visited") && ('nodes_visited' in item))
          var timeline_skill = $('<p>', { text:"[" + item.nodes_visited.join(',') + "]"}).addClass("botvis-timeline-botprops-nodevisited").appendTo(timeline_bot_props);   

        // iterate over messages
        
        var timeline_agent = $('<h4>', { text: '[ ' + item.agent + ' ]' }).addClass("botvis-timeline-heading").appendTo(timeline_heading);
        
        for (var i=0;i<item.messages.length;i++) {
          //var timeline_body = $('<div>').addClass("botvis-timeline-body").appendTo(timeline_panel);
          var timeline_bodytext = $('<p>', { text: item.messages[i].text }).appendTo(timeline_body);
          //var timeline_bodyprops = $('<div>').addClass("botvis-timeline-bodyprops").appendTo(timeline_body);
          if ('buttons' in item.messages[0])
            var timeline_bodybuttons = $('<p>', { text:item.messages[i].buttons}).addClass("botvis-timeline-bodyprops-buttons").appendTo(timeline_body);
        }
        var timeline_time = $('<p>', { text: item.timestamp }).addClass("botvis-timeline-time").appendTo(timeline_panel);

        return;
      });
    };

    // var transcriptSample = [{
    //   conversation: {
    //     id: "jshd6723",
    //     props: { "attr": "value" },
    //     agents: [{ "user": "user 1", "skill1": "skill 1" }]
    //   },
    //   events: [{
    //     timestamp: "2014-05-05T12:12:12:000Z",
    //     id: "112312",
    //     agent: "user", // or skill1
    //     channel: "",
    //     type: "request", // response, handoff, internal
    //     intents: [{ intent: "greeting", confidence: 0.85 }],
    //     entities: [{ entity: "entity1", confidence: 0.25 }],
    //     messages: [{
    //       text: "some text to display",
    //       attachments: [{
    //         type: "button",
    //         buttons: [{
    //           text: "button1"
    //         },
    //         {
    //           type: "button",
    //           buttons: [{
    //             text: "button1"
    //           }]
    //         }]
    //       }]
    //     }]
    //   }, {
    //     timestamp: "2014-05-05T12:12:12:000Z",
    //     id: "112312",
    //     agent: "bot", // or skill1
    //     channel: "",
    //     type: "response", // response, handoff, internal
    //     intents: [{ intent: "greeting", confidence: 0.85 }],
    //     entities: [{ entity: "entity1", confidence: 0.25 }],
    //     messages: [{
    //       text: "Howdy, how are you today?",
    //       attachments: [{
    //         type: "button",
    //         buttons: [{
    //           text: "button1"
    //         },
    //         {
    //           type: "button",
    //           buttons: [{
    //             text: "button1"
    //           }]
    //         }]
    //       }]
    //     }]
    //   }]
    // }];

    var defaultConfig = {
      display_fields: ['turn_label', 'nodes_visited_str', 'nodes_visited'],
      margin: { top: 20, right: 90, bottom: 30, left: 120 },
      width: 1000,
      height: 600,
    };

    var _container = container;

    _config = $.extend(true, defaultConfig, config); // merge the default with the incoming config.

    // if one conversation passed, put it in an array
    if (!Array.isArray(data)){
      _data = [data];
    } else {
      _data = data;
    }
    
    _chart.config = _config;
    _chart.data = _data;
    _chart.selected = 0;
    _chart.container = _container;

    // bot analytics header
    var baHeader = $('<div>').addClass("botvis-ba-header").appendTo(_chart.container);
    $('<a>', { text: 'IBM Conversation Analytics Toolkit | Transcript Visualizer' }).addClass("botvis-ba-label").appendTo(baHeader);
    // create container
    var transcriptContainer = $('<div>').addClass("botvis-transcript-container").appendTo(_chart.container);
    // create header
    var conversationHeader = $('<div>').addClass("botvis-conversation-header").appendTo(transcriptContainer);
    var conversationBody = $('<div>').addClass("botvis-conversation-body").appendTo(transcriptContainer);
    _chart.conversationBody = conversationBody;

    var clickedNavButton = function(event){
      return function(event){
        if (event.data.command == "start") 
          _chart.selected = 0; 
        else if (event.data.command == "next") {
          if (_chart.selected < _chart.data.length -1) 
            _chart.selected++;
        } else if (event.data.command == "prev") {
          if (_chart.selected > 0) 
            _chart.selected--;
        } else if (event.data.command == "end")
            _chart.selected = _chart.data.length-1
        _chart.drawSelectedConversation();
      }
    }();

    $('<span>', { text: 'Conversation id: ' }).appendTo(conversationHeader);
    $('<button>', { text:'|<'}).addClass("ui-button ui-widget ui-corner-all").click({command: "start"}, clickedNavButton).appendTo(conversationHeader);
    $('<button>', { text:'<<'}).addClass("ui-button ui-widget ui-corner-all").click({command: "prev"}, clickedNavButton).appendTo(conversationHeader);
    _chart.conversation_span = $('<span>').addClass("botvis-conversation-id").appendTo(conversationHeader);
    //_chart.conversation_span.text(_chart.data[0].conversation.id + " (" + _chart.selected+1  + " of " + _chart.data.length + ")" );
    $('<button>', { text:'>>'}).addClass("ui-button ui-widget ui-corner-all").click({command: "next"}, clickedNavButton).appendTo(conversationHeader);
    $('<button>', { text:'>|'}).addClass("ui-button ui-widget ui-corner-all").click({command: "end"}, clickedNavButton).appendTo(conversationHeader);
   
    _chart.drawSelectedConversation();

  };

  return draw;

});
