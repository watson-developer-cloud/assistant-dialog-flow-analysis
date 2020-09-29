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

require.undef('wa_dialog_chart');
define('wa_dialog_chart', [ 'wa_model', 'wa_tree', 'wa_node_details', 'd3' ], function (wa_model, Tree, NodeDetails, d3) {
  function draw (container, config, data) {
    //debugger;
    let visits = null;
    if ("visits" in data)
      visits = new wa_model.Visits(JSON.parse(data.visits));
    const ws = new wa_model.Workspace(data.workspace);
    const state = {
      search: {
        foundNodeIds: [],
        foundNodeId: undefined
      },
      ws
    };

    const defaultConfig = {
      margin: { top: 20, right: 90, bottom: 30, left: 120 },
      width: 1200,
      height: 800,
      title: ""
    };

    const _container = container;
    const _config = $.extend(true, defaultConfig, config); // merge the default with the incoming config.

    const _chart = {
      container: _container,
      config: _config
    }

    if (config["debugger"]===true){
      debugger;
    }
    
    // bot analytics header
    const baHeader = $('<div>')
      .addClass("botvis-ba-header")
      .appendTo(_chart.container);
    $('<a>', { text: 'IBM Conversation Analytics Toolkit | Watson Assistant Dialog' })
      .addClass("botvis-ba-label")
      .appendTo(baHeader);

    d3.select(_container[ 0 ])
      .selectAll("*")
      .remove();

    const search_div = d3.select(_chart.container)
      .append("div")
      .attr("class", "searchArea");

    const bodyContainer = d3.select(_chart.container)
      .append("div")
      .attr("class", "body_container");


    const tree = new Tree(bodyContainer.append("div").node(), {});
    const details = new NodeDetails(bodyContainer.append("div").node());


    tree.on(Tree.EVENT_SELECTED_NODE_CHANGED, node => details.show(node));
    details.on(NodeDetails.EVENT_JUMP_TO_NODE, node_id => {
      tree.select(ws.nodeById(node_id));
      tree.scrollToNode(node_id);
    });
    // tree.on(Tree.EVENT_TURNS_CLICKED, (ts, node) => console.log(ts.length));
    addSearch(search_div, tree);

    tree.showWSTree(ws, visits);

    function addSearch (container, tree) {
      container.append('label')
        .attr('for', 'searchNode')
        .text('Search Node');
      container.append('input')
        .attr('id', 'searchNode')
        .attr('name', 'searchNode')
        .property('type', 'text')
        .on('input', (d, i, g) => {
          const str = d3.select(g[ i ]).property('value');
          searchNode(str);
        });
      const counter = container.append('span');
      container.append('input')
        .property('type', 'button')
        .property('value', '<')
        .on('click', () => searchNext(-1));
      container.append('input')
        .property('type', 'button')
        .property('value', '>')
        .on('click', () => searchNext(1));

      function searchNext (delta) {
        const { foundNodeId, foundNodeIds } = state.search;
        if (foundNodeIds.length === 0) {
          counter.text('0');
          return
        }
        const index = foundNodeIds.indexOf(foundNodeId);
        let nextIndex = index + delta;
        nextIndex = nextIndex === foundNodeIds.length ? 0 : nextIndex;
        nextIndex = nextIndex === -1 ? foundNodeIds.length - 1 : nextIndex;
        const nextFoundNodeId = foundNodeIds[ nextIndex ]
        state.search.foundNodeId = nextFoundNodeId;
        counter.text(`${ nextIndex + 1 }/${ foundNodeIds.length }`);
        tree.classNodes([ nextFoundNodeId ], 'currentSearchResult');
        tree.scrollToNode(nextFoundNodeId);
      }
      function searchNode (term) {
        if (term.length == 0) {
          state.search.foundNodeIds = [];
          tree.classNodes([], 'searchResult');
          counter.text('');
          return;
        }
        if (state.ws) {
          const foundNodes = state.ws.nodes()
            .filter(n => n.match(term));
          state.search = {
            foundNodeIds: foundNodes.map(n => n.id),
            foundNodeId: undefined
          };
          foundNodes.forEach(n => tree.expand(n));
          tree.classNodes(state.search.foundNodeIds, 'searchResult');
          setTimeout(() => searchNext(1), 0);
        }
      }
    }

    return _chart;
  }

  return draw;
});
