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

require.undef('wa_node_details');
define('wa_node_details', [ 'wa_model', 'd3' ], function ({ EventPublisher, Workspace }, d3) {

  const FEEDBACK_TIMEOUT = 4000; //4 secs
  const COPY_SVG = '<svg focusable="false" preserveAspectRatio="xMidYMid meet" xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 32 32" aria-hidden="true"><path d="M28,10V28H10V10H28m0-2H10a2,2,0,0,0-2,2V28a2,2,0,0,0,2,2H28a2,2,0,0,0,2-2V10a2,2,0,0,0-2-2Z"></path><path d="M4,18H2V4A2,2,0,0,1,4,2H18V4H4Z"></path><title>Copy</title></svg>'

  function copyToClipboard (txt) {
    const dummy = document.createElement("textarea");
    document.body.appendChild(dummy);
    dummy.value = txt;
    dummy.select();
    document.execCommand("copy");
    document.body.removeChild(dummy);
  }

  class NodeDetails extends EventPublisher {
    constructor (dom) {
      super();
      this._container =d3.select(dom).classed('node_details', true);
      this._container.append('div')
      .classed('infodiv-title', true)
      .text("Selection Details:");
    }
    clear () {
      this._container.selectAll('*').remove();
    }
    show (node) {
      this.clear();
      this._container.append('div')
        .classed('infodiv-title', true)
        .text("Selection Details:");
      this._addName(node);
      this._addNodeId(node);
      this._addType(node);
      this._addCondition(node);
      this._addResponse(node);
      this._addContext(node);
      this._addJumpTo(node);
    }
    _addName (node) {
      const entry = this._container.append('div')
        .classed('entry', true);
      entry.append('div')
        .classed('key', true)
        .text("Name:");
      entry.append('div')
        .classed('value', true)
        .text(node.title);
    }
    _addNodeId (node) {
      const entry = this._container.append('div')
        .classed('entry', true);
      entry.append('div')
        .classed('key', true)
        .text("Node Id:");
      this._addCopiedValue(entry, node.id, 'Copy this node Id');
    }
    _addCopiedValue (parent, value, title) {
      let timeout_id = undefined;
      const valElem = parent.append('div')
        .classed('value copy', true)
        .text(value);
      valElem.append('span')
        .classed('copy__feedback', true)
        .text('Copied!');

      function cleanFeedback () {
        valElem.classed('feedback', false);
        timeout_id = undefined;
      }
      parent.append('button')
        .classed('copy_btn', true)
        .html(COPY_SVG)
        .attr('title', title)
        .on('click', () => {
          d3.event.stopPropagation();
          copyToClipboard(value);
          if (timeout_id) {
            clearTimeout(timeout_id);
            cleanFeedback();
          }
          valElem.classed('feedback', true);
          timeout_id = setTimeout(cleanFeedback, FEEDBACK_TIMEOUT);
        });
    }
    _addType (node) {
      const entry = this._container.append('div')
        .classed('entry', true);
      entry.append('div')
        .classed('key', true)
        .text("Type:");
      entry.append('div')
        .classed('value', true)
        .text(node.type);
    }
    _addCondition (node) {
      const entry = this._container.append('div')
        .classed('entry', true);
      entry.append('div')
        .classed('key', true)
        .text("Condition:");
      this._addCopiedValue(entry, node.condition, 'Copy this node condition');
    }
    _addResponse (node) {
      if (!node.output) {
        return;
      }
      const output = node.output.generic || node.output.text && (node.output.text.values || [ node.output.text ]);
      const entry = this._container.append('div')
        .classed('entry', true);
      entry.append('div')
        .classed('key', true)
        .text("Response:");
      this._addCopiedValue(entry, JSON.stringify(output, null, 2), 'Copy this node output');
    }
    _addContext (node) {
      if (!node.context) {
        return;
      }
      const entry = this._container.append('div')
        .classed('entry', true);
      entry.append('div')
        .classed('key', true)
        .text("Set Context:");
      this._addCopiedValue(entry, JSON.stringify(node.context, null, 2), 'Copy this node context');
    }
    _addJumpTo (node) {
      if (!node.nextStep) {
        return;
      }
      const entry = this._container.append('div')
        .classed('entry', true);
      entry.append('div')
        .classed('key', true)
        .text("Next Step:");
      if (node.nextStep.behavior === Workspace.JUMP_TO) {
        const val = entry.append('div')
          .classed('value', true);
        val.append('span')
          .text(node.nextStep.behavior);
        val.append('a')
          .attr('href', 'javascript:')
          .on('click', d => {
            this._publish(NodeDetails.EVENT_JUMP_TO_NODE, node.nextStep.dialog_node);
          })
          .text(node.nextStep.dialog_node);
        val.append('span').text(node.nextStep.selector);
      }
      else {
        entry.append('div')
          .classed('value', true)
          .text(node.nextStep.behavior);
      }
    }
  }
  NodeDetails.EVENT_JUMP_TO_NODE = 'jump_to';

  return NodeDetails;
});
