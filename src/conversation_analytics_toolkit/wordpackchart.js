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

require.undef('wordpackchart');

define('wordpackchart', ['d3'], function (d3) {
  //debugger;

  function draw(container, config, data) {

    if (config["debugger"] === true) {
      debugger;
    }

    var _config = {}, _chart = {}, _data = null;

    var _container = container;

    var target = Array.isArray(data) ? [] : {};
    _data = $.extend(true, target, data); // make a copy of the data so we can update it

    _chart.container = _container;
    _chart.config = _config;

    var defaultConfig = {
      margin : {top: 20, right: 90, bottom: 30, left: 120},
      flattened: false,
      width : 1200,
      height : 800
    };
    _config = $.extend(true, defaultConfig, config);

    var margin = _config.margin,
          width = _config.width - _config.margin.left - _config.margin.right,
          height = _config.height - _config.margin.top - _config.margin.bottom;

    // bot analytics header
    var baHeader = $('<div>').addClass("botvis-ba-header").appendTo(_chart.container);
    $('<a>', { text: 'IBM Conversation Analytics Toolkit | Wordpack Visualization' }).addClass("botvis-ba-label").appendTo(baHeader);

    var svg = d3.select(_container).append("svg")
          .attr("class", "botvis wordpackchart")
          .attr("width", _config.width)
          //.attr("width", width + margin.right + margin.left)
          .attr("height", height + _config.margin.top + _config.margin.bottom);

    _chart.svg = svg;

    var g = svg.append("g")
      .attr("transform", "translate("
      + _config.margin.left + "," + _config.margin.top + ")");

    var packLayout = d3.pack()
      .size([width, height])
      .padding(2);
              
    var rootNode = d3.hierarchy(_data);
    
    rootNode.sum(function(d) {
      return d.value;
    });

    packLayout(rootNode);
    
    var nodes_data = _config.flattened? rootNode.leaves() : rootNode.descendants()
    //var nodes_data = rootNode.descendants()

    var nodes = g
      .selectAll('g')
      .data(nodes_data)
      .enter()
      .append('g')
      .attr('transform', function(d) {return 'translate(' + [d.x, d.y] + ')'})
    
    nodes
      .append('circle')
      .attr('class', 'group')
      .attr('r', function(d) { return d.r; })
    
    nodes
      .append('text')
      .attr('class', 'word')
      .text(function(d) {
        return d.children === undefined ? d.data.name : '';
      })
      .style("font-size", function(d) { 
        return Math.min(2 * d.r, (2 * d.r - 8) / this.getComputedTextLength() * 11) + "px"; 
      })
      .attr("dy", ".30em");   
    
    nodes
      .append('text')
      .attr('class', 'wordcount')
      .text(function(d) {
        return d.children === undefined ? d.value : '';
      })
      .style("font-size", function(d) { 
        return Math.min(1.5 * d.r, (2 * d.r - 8) / this.getComputedTextLength() * 2.5) + "px"; 
      })
      .attr("dy", "1.5em");
  };

  return draw;

});
