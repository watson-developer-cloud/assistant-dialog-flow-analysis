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

require.undef('wa_model');
define('wa_model', [], function () {

  /*****ES6 Polyfill*****/
  const reduce = Function.bind.call(Function.call, Array.prototype.reduce);
  const isEnumerable = Function.bind.call(Function.call, Object.prototype.propertyIsEnumerable);
  const concat = Function.bind.call(Function.call, Array.prototype.concat);
  const keys = Reflect.ownKeys;

  if (!Object.values) {
    Object.values = function values (O) {
      return reduce(keys(O), (v, k) => concat(v, typeof k === 'string' && isEnumerable(O, k) ? [ O[ k ] ] : []), []);
    };
  }

  if (!Object.entries) {
    Object.entries = function entries (O) {
      return reduce(keys(O), (e, k) => concat(e, typeof k === 'string' && isEnumerable(O, k) ? [ [ k, O[ k ] ] ] : []), []);
    };
  }
  /************/

  class EventPublisher {
    constructor () {
      this._handlers = {};
    }
    on (eventName, callback) {
      if (!this._handlers[ eventName ]) {
        this._handlers[ eventName ] = [];
      }
      this._handlers[ eventName ].push(callback);
    }
    _publish (eventName, ...args) {
      // console.log(eventName);
      const hs = this._handlers[ eventName ] || [];
      return Promise.all(
        hs.map(h => h.call(this, ...args))
      );
    }
  }

  class Turn {
    constructor (json) {
      this.json = json;
      this.conv = undefined;
    }
    setConversation (conv) {
      this.conv = conv;
    }
    get id () {
      return this.json[ '@metadata' ].tx_id;
    }
    get conversation () {
      return this.conv;
    }
    get request () {
      return this.json.payload.request;
    }
    get response () {
      return this.json.payload.response
    }
    get conversationMetadata () {
      return this.json.metadata.conversation;
    }
    get conversationId () {
      return this.conversationMetadata.conversation_id;
    }

    get workspaceId () {
      return this.conversationMetadata.workspace_id;
    }

    get turnCounter () {
      return this.conversationMetadata.turn_counter;
    }

    get startTime () {
      return this.request.timestamp;
    }
    get inputText () {
      return this.request.input && this.request.input.text;
    }
    get requestContext () {
      return this.request.context;
    }
    get visitedNodeIds () {
      const nodes_visited = [ ...this.response.output.nodes_visited ]; //copy

      //response condition (MCR) dont appear in the nodes_visited
      const reqOutputs = Object.keys(_.get(this.requestContext, 'system._node_output_map', {}));
      const respOutputs = Object.keys(_.get(this.responseContext, 'system._node_output_map', {}));
      respOutputs
        .filter(key => !reqOutputs.includes(key))
        .forEach(key => {
          if (!nodes_visited.includes(key)) {
            nodes_visited.push(key);
          }
        });
      return nodes_visited;
    }
    get outputText () {
      return this.response.output.text;
    }
    get responseContext () {
      return this.response.context;
    }
    get intents () {
      return this.response.intents;
    }
    get entities () {
      return this.response.entities;
    }
    isLastTurn (node) {
      return (this.conversation.turns().length === this.turnCounter) && (last(this.visitedNodeIds) === node.id);
    }
  }

  class AYTurn extends Turn {

    get request () {
      return this.json.request;
    }

    get response () {
      return this.json.response
    }
    get conversationId () {
      return this.response.context.conversation_id;
    }
    get workspaceId () {
      return this.json.workspace_id;
    }
    get turnCounter () {
      return this.responseContext.system.dialog_request_counter;
    }
    get startTime () {
      return this.json.request_timestamp;
    }
  }

  class Conversation {
    constructor (wsId, convId, turns) {
      this._convId = convId;
      this._wsId = wsId;
      this._turnsMap = {};
      turns.sort((a, b) => a.turnCounter - b.turnCounter);
      this._turns = turns;
      turns.forEach(turn => {
        this._turnsMap[ turn.turnCounter ] = turn;//last only
        turn.setConversation(this);
      });
    }
    get id () {
      return this._convId;
    }
    get workspaceId () {
      return this._wsId;
    }
    turns () {
      return this._turns;
    }
    turnByCounter (counter) {
      return this._turnsMap[ counter ];
    }
    get firstTurnStartTime () {
      return this.turns()[ 0 ].startTime;
    }
  }
  class Workspace {
    constructor (json) {
      this.json = json;
      this._nodeById = {};
      this.json.dialog_nodes.forEach(n => {
        this._nodeById[ n.dialog_node ] = new WsNode(n, this);
      });
      this._nodes = this._sortNodes(Object.values(this._nodeById), undefined);
    }
    get id () {
      return this.json.workspace_id;
    }
    get name () {
      return this.json.name;
    }
    get description () {
      return this.json.description;
    }
    nodes () {
      return this._nodes;
    }
    _sortNodes (nodes, parent) {
      const rs = [];
      const ns = nodes.filter(n => n.parentId === parent);
      const first = ns.find(n => !n.prevSiblingId);
      let cur = first;
      while (cur) {
        rs.push(cur);
        rs.push(...this._sortNodes(nodes, cur.id));
        cur = ns.find(n => n.prevSiblingId === cur.id);
      }
      return rs;
    }
    nodeById (id) {
      return this._nodeById[ id ];
    }
  }

  //static members
  Workspace.NODE_TYPE_FOLDER = 'folder';
  Workspace.NODE_TYPE_FRAME = 'frame';
  Workspace.NODE_TYPE_RESPONSE_CONDITION = 'response_condition';
  Workspace.NODE_TYPE_STANDARD = 'standard';
  Workspace.NODE_TYPE_SLOT = 'slot';
  Workspace.NODE_TYPE_EVENT_HANDLER = 'event_handler';
  Workspace.JUMP_TO = 'jump_to';
  Workspace.SKIP_USER_INPUT = 'skip_user_input';
  Workspace.RESPONSE_CONDITION = 'response_condition';

  class WsNode {
    constructor (json, ws) {
      this.json = json;
      this.ws = ws;
    }
    get id () {
      return this.json.dialog_node;
    }
    get type () {
      return this.json.type;
    }
    get title () {
      switch (this.type) {
        case Workspace.NODE_TYPE_SLOT: return this.json.variable;
        case Workspace.NODE_TYPE_EVENT_HANDLER: return this.json.event_name;
        default: return this.json.title;
      }
    }
    get titleOrId () {
      return this.title || this.id;
    }
    get context () {
      return this.json.context;
    }
    get condition () {
      return this.json.conditions;
    }
    get output () {
      return this.json.output;
    }
    get outputLongText () {
      const vals = this.output && this.output.text && (this.output.text.values || [ this.output.text ]) || [];
      const texts = vals.map(val => JSON.stringify(val, null, 2));
      return texts.join(', ');
    }
    get nextStep () {
      return this.json.next_step;
    }
    get prevSiblingId () {
      return this.json.previous_sibling;
    }
    get parentId () {
      return this.json.parent;
    }
    parent () {
      return this.ws.nodeById(this.parentId);
    }
    isParent () {
      return this.ws.nodes().find(n => n.parentId === this.id);
    }
    isTop () {
      return !this.parentId;
    }
    isEndOfTurn () {
      return !(this.isJumpTo() || this.isFolder() || this.isSwitch());
    }
    isFrame () {
      return Boolean(this.type === Workspace.NODE_TYPE_FRAME);
    }
    isJumpTo () {
      return Boolean(this.nextStep && this.nextStep.behavior === Workspace.JUMP_TO);
    }
    isSwitch () {
      return Boolean((!this.isFrame()) && this.json.metadata && this.json.metadata._customization && this.json.metadata._customization.mcr);
    }
    isFolder () {
      return this.type === Workspace.NODE_TYPE_FOLDER;
    }
    directChildren () {
      return this.ws.nodes().filter(n => n.parentId === this.id);
    }
    depth () {
      if (this.isTop()) {
        return 0;
      }
      return this.parent().depth() + 1;
    }

    match (str) {
      return stringContains(this.id, str) ||
        stringContains(this.title, str) ||
        stringContains(this.condition, str) ||
        stringContains(this.type, str) ||
        stringContains(JSON.stringify(this.json.metadata), str) ||
        stringContains(JSON.stringify(this.output), str)
    }
  }
  function stringContains (bigStr, smallStr) {
    if (bigStr && smallStr) {
      return bigStr.toLowerCase().indexOf(smallStr.toLowerCase()) >= 0
    }
    return false;
  }

  function last (arr) {
    return arr[ arr.length - 1 ];
  }

  return {
    Workspace,
    Conversation,
    Turn: AYTurn,
    EventPublisher
  }
});