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

require.undef('wa_tree');
define('wa_tree', [ 'wa_model', 'd3' ], function ({ Workspace, EventPublisher }, d3) {


  function replaceAll (str, find, replace) {
    return str.replace(new RegExp(find, 'g'), replace);
  }

  class Tree extends EventPublisher {
    constructor (treeDom, settings) {
      super();
      this._treeDom = d3.select(treeDom).classed("wa_tree", true);
      this._settings = settings;
      this._ws = undefined;
      this._visits = undefined;
      this._convs = undefined;
      this._selectedNode = undefined;
      this._visitsByNodeId = undefined;
    }

    showStats () {
      this._treeDom.classed('visits', false);
    }

    scrollToNode (nodeId) {
      const node = d3.select(this.nodeRef(nodeId));
      if (!node.empty()) {
        // node.node()
        //   .scrollIntoView(false);
        node.node()
          .scrollIntoView({ block: 'center', behavior: 'smooth' });
      }
    }
    classNodes (nodeIds, clazz) {
      d3.selectAll('.node')
        .classed(clazz, (d) => nodeIds.includes(d.id));
    }
    showVisitedNodes (visitedNodeIds) {
      this._treeDom.classed('visits', true);
      d3.selectAll('.turn_visit').remove();
      if (visitedNodeIds.length > 0) {
        this._markTurnVisits(visitedNodeIds);
        this._ws.nodes().forEach(n => {
          if (visitedNodeIds.includes(n.id)) {
            this.expand(n);
          }
        });
        this.scrollToNode(visitedNodeIds[ 0 ]);
      }
    }
    showWSTree (ws, visits) {
      this._ws = ws;
      this._visits = visits;
      this._treeDom.classed('visits', false);
      this.renderNodes();
      this.collapseAll();
    }
    showVisits (convs) {
      this._convs = convs;
      this._visitsByNodeId = turnsByVisitedNode(convs);
      this._markAbandoned(this._treeDom.selectAll(".node"));
      this._markStats(this._treeDom.selectAll(".node"));
    }

    // Toggle expand collapse on nodeClicked.
    expandCollapseClicked (d) {
      d3.event.stopPropagation();
      if (d.collapsed) {
        this.expand(d);
      } else {
        this.collapse(d);
      }
    }
    nodeRef (id) {
      return replaceAll('#' + id, ' ', '_');
    }
    expand (d) {
      d.directChildren().forEach(c => {
        d3.select(this.nodeRef(c.id))
          .classed('hidden', false);
      });
      d.collapsed = false;
      d3.select(this.nodeRef(d.id)).classed('node-container--expanded', true);
      if (d.parent()) {
        this.expand(d.parent());
      }
    }

    collapse (d) {
      d.collapsed = true;
      d3.select(this.nodeRef(d.id)).classed('node-container--expanded', false);
      d.directChildren().forEach(c => {
        this.collapse(c);
        d3.select(this.nodeRef(c.id))
          .classed('hidden', true);
      });
    }
    expandAll () {
      this._ws.nodes()
        // .filter(n => n.isTop())
        .forEach(n => this.expand(n));
    }
    collapseAll () {
      this._ws.nodes()
        .filter(n => n.isTop())
        .forEach(n => this.collapse(n));
    }
    select (d) {
      if (this._selectedNode) {
        d3.select(this.nodeRef(this._selectedNode.id)).classed('node--selected', false);
      }
      this._selectedNode = d;
      d3.select(this.nodeRef(this._selectedNode.id)).classed('node--selected', true);
      this._publish(Tree.EVENT_SELECTED_NODE_CHANGED, d);
    }

    _markStats (selection) {
      const visitsAtNode = d => this._visitsByNodeId.get(d.id);
      selection
        .filter(d => visitsAtNode(d))
        .append('div')
        .classed('marker', true)
        .classed('this_turn', true)
        .text(d => visitsAtNode(d).length)
        .attr('title', 'Number of turns that visited this node')
        .on("click", d => {
          d3.event.stopPropagation();
          this._publish(Tree.EVENT_TURNS_CLICKED, visitsAtNode(d), d);
        });
    }
    _markAbandoned (selection) {
      const nodeIdsToAbandonedTurns = {};
      abandonedConversationsAtNodes(this._convs)
        .forEach(([ k, v ]) => nodeIdsToAbandonedTurns[ k ] = v);

      const visitsAtNode = d => nodeIdsToAbandonedTurns[ d.id ] || [];
      selection
        .filter(d => visitsAtNode(d).length > 0)
        .append('div')
        .classed('marker', true)
        .classed('abandoned', true)
        .text(d => visitsAtNode(d).length)
        .attr('title', 'Number of turns ABANDONED after this node')
        .on("click", d => {
          d3.event.stopPropagation();
          this._publish(Tree.EVENT_TURNS_CLICKED, visitsAtNode(d), d);
        });
    }
    _markTurnVisits (visitedNodeIds) {
      const domIds = visitedNodeIds.map(id => this.nodeRef(id)).join(', ');
      const marker = d3.selectAll(domIds)
        .filter(d => visitedNodeIds.includes(d.id))
        .append('div')
        .classed('marker', true)
        .classed('turn_visit', true);
      const go = delta =>
        (d, myIndex) => {
          d3.event.stopPropagation();
          const nextIndex = myIndex + delta;
          const nextNodeId = visitedNodeIds[ nextIndex ];
          this.scrollToNode(nextNodeId);
        };
      function arrow_right (selection) {
        selection.append('svg')
          .attr('width', 8)
          .attr('height', 12)
          .attr('viewBox', '0 0 8 12')
          .append('path')
          .attr('d', 'M0 10.6L4.7 6 0 1.4 1.4 0l6.1 6-6.1 6z');
      }
      arrow_right(
        marker
          .filter((d, i) => i > 0)
          .append('span')
          .classed('nav prev', true)
          .on("click", go(-1))
      );
      marker
        .append('span')
        .classed('marker_value', true)
        .text(d => visitedNodeIds.indexOf(d.id) + 1);
      arrow_right(
        marker
          .filter((d, i, group) => i < group.length - 1)
          .append('span')
          .classed('nav next', true)
          .on("click", go(1))
      );
    }
    renderNodes () {
      const nodes = this._ws.nodes();

      this._treeDom.selectAll(".node").remove();
      const node = this._treeDom.selectAll(".node")
        .data(nodes, d => d.id);

      const nodeContainer = node.enter()
        .append('div')
        .classed('node-container', true)
        .append("div")
        .attr('id', d => replaceAll(d.id, ' ', '_'))
        .classed("node", true)
        .classed('parent', d => d.isParent())
        .classed("eot", d => d.isEndOfTurn())
        .style("transform", (d) =>
          `translateX(${ d.depth() * 20 }px)`
        )
        .on('click', d => {
          d3.event.stopPropagation();
          this.select(d);
        });
      nodeContainer
        .append('div')
        .classed('node__expander', true)
        .append('button')
        .attr('type', 'button')
        .attr('title', 'click to expand/collapse')
        .on('click', d => this.expandCollapseClicked(d))
        .append('svg')
        .attr('width', d => d.isFolder() ? 16 : 8)
        .attr('height', 12)
        .attr('viewBox', d => d.isFolder() ? '0 0 16 12' : '0 0 8 12')
        .append('path')
        .attr('d', d => d.isFolder() ? 'M0 12h16V2H8V0H0z' : 'M0 10.6L4.7 6 0 1.4 1.4 0l6.1 6-6.1 6z');

      const nodeContent = nodeContainer
        .append('div')
        .classed('node__contents', true);

      this.createTitle(nodeContent);

      this.createConditionElem(nodeContent);
      this.createOutputElem(nodeContent);
      this.createBottomElem(nodeContent);
      if (this._visits != null)
        this.createStatsElem(nodeContent);
    }
    createBottomElem(nodeContent) {
      const bottom = nodeContent.append("div")
        .classed("node__subtext", true);
      bottom
        .append("div")
        .attr("class", "set_context")
        .text(d => {
          const vals = Object.values(d.context || {});
          if (vals.length > 0) {
            return `${ vals.length } Context Set`;
          }
        })
        .attr('title', d => JSON.stringify(d.context));

      const jumpTo = bottom
        .filter(d => d.nextStep)
        .append("div")
        .classed("jump_to", true);
      jumpTo.append('span')
        .text(d => d.nextStep.behavior);
      jumpTo.append('a')
        .attr('href', 'javascript:')
        .on('click', d => {
          const target = this._ws._nodeById[ d.nextStep.dialog_node ]
          this.expand(target);
          setTimeout(() => { 
            this.select(target);
            this.scrollToNode(target.id);
          });
        })
        .text(d => d.nextStep.dialog_node);
      jumpTo.append('span')
        .text(d => d.nextStep.selector);

      return bottom;
    }

    createStatsElem(nodeContent){
      //debugger;
      const stats = nodeContent.append("div")
        .classed("node__stats", true)
        .text("visits: ");
      stats
        // .filter(d => !d.nextStep)
        .append("div")
        .attr("class", "stats")
        .text(d => {
          //debugger;
          return this._visits.nodeVisits(d.id);
        })
      return stats
    }

    createOutputElem(nodeContent){
      return nodeContent
        // .filter(d => !d.nextStep)
        .append("div")
        .attr("class", "output")
        .classed("node__subtext", true)
        .text(d => {
          if (d.isSwitch()) {
            return ' SWITCH ';
          }
          if (d.outputLongText)
            return d.outputLongText;
        })
        .attr('title', d => d.outputLongText);
    }
    createConditionElem(nodeContent){
      return nodeContent.append("div")
      .attr("class", "node__subtext")
      .append("div")
      .text(d => {
        const cond = d.condition;
        return cond
      })
      .classed("cond", true)
      .attr("title", d => d.condition);
    }
    createTitle (nodeContent) {
      const title = nodeContent.append("div")
        .attr("class", "node__text")
        .attr("title", d => `${ d.title } (${ d.id })`);
      const EMPTY_TITLE = '_';
      title.append('span')
        .text(d => {
          const titleTxt = d.title || EMPTY_TITLE;
          switch (d.type) {
            case Workspace.NODE_TYPE_FRAME:
              return `FRAME: ${ titleTxt }`;
            case Workspace.NODE_TYPE_SLOT:
              return `SLOT: ${ titleTxt }`;
            case Workspace.NODE_TYPE_EVENT_HANDLER:
              return `EVENT: ${ titleTxt }`;
            case Workspace.NODE_TYPE_RESPONSE_CONDITION:
              return `RESP_COND: ${ titleTxt }`;
            default: return titleTxt;
          }
        });
      return title;
    }
  }
  Tree.EVENT_TURNS_CLICKED = 'turns_clicked';
  Tree.EVENT_SELECTED_NODE_CHANGED = 'node_selected';

  return Tree;
});