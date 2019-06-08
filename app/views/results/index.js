let socket = io(window.location.host);

// function getNeighbors(node) {
//   return window.baseBranches.reduce(function (neighbors, link) {
//       if (link.target.id === node.id) {
//         neighbors.push(link.source.id)
//       } else if (link.source.id === node.id) {
//         neighbors.push(link.target.id)
//       }
//       return neighbors
//     },
//     [node.id]
//   )
// }
// function isNeighborLink(node, link) {
//   return link.target.id === node.id || link.source.id === node.id
// }
// function getNodeColor(node, neighbors) {
//   if (Array.isArray(neighbors) && neighbors.indexOf(node.id) > -1) {
//     return 'blue'
//   }
//   return 'red'
// }
// function getLinkColor(node, link) {
//   return isNeighborLink(node, link) ? 'green' : '#E5E5E5'
// }
// function getTextColor(node, neighbors) {
//   return Array.isArray(neighbors) && neighbors.indexOf(node.id) > -1 ? 'green' : 'black'
// }
// var width = window.innerWidth
// var height = window.innerHeight
// var svg = d3.select('svg')
// svg.attr('width', width).attr('height', height)
// var linkElements,
//   nodeElements,
//   textElements
// // we use svg groups to logically group the elements together
// var linkGroup = svg.append('g').attr('class', 'links')
// var nodeGroup = svg.append('g').attr('class', 'nodes')
// var textGroup = svg.append('g').attr('class', 'texts')

// // we use this reference to select/deselect
// // after clicking the same element twice
// var selectedId

// // simulation setup with all forces
// var linkForce = d3
//   .forceLink()
//   .id(function (link) { return link.id })
//   .strength(function (link) { return link.strength })

// var simulation = d3
//   .forceSimulation()
//   .force('link', linkForce)
//   .force('charge', d3.forceManyBody().strength(-120))
//   .force('center', d3.forceCenter(width / 2, height / 2))

// var dragDrop = d3.drag().on('start', function (node) {
//   node.fx = node.x
//   node.fy = node.y
// }).on('drag', function (node) {
//   simulation.alphaTarget(0.7).restart()
//   node.fx = d3.event.x
//   node.fy = d3.event.y
// }).on('end', function (node) {
//   if (!d3.event.active) {
//     simulation.alphaTarget(0)
//   }
//   node.fx = null
//   node.fy = null
// })

// // select node is called on every click
// // we either update the data according to the selection
// // or reset the data if the same node is clicked twice
// function selectNode(selectedNode) {
//     console.log('handle node select')
//   // if (selectedId === selectedNode.id) {
//   //   selectedId = undefined
//   //   resetData()
//   //   render()
//   // } else {
//   //   selectedId = selectedNode.id
//   //   updateData(selectedNode)
//   //   render()
//   // }
//   // var neighbors = getNeighbors(selectedNode)
//   // // we modify the styles to highlight selected nodes
//   // nodeElements.attr('fill', function (node) { return getNodeColor(node, neighbors) })
//   // textElements.attr('fill', function (node) { return getTextColor(node, neighbors) })
//   // linkElements.attr('stroke', function (link) { return getLinkColor(selectedNode, link) })
// }

// // this helper simple adds all nodes and links
// // that are missing, to recreate the initial state
// function resetData() {
//   var nodeIds = window.nodes.map(function (node) { return node.id })
//   window.baseNodes.forEach(function (node) {
//     if (nodeIds.indexOf(node.id) === -1) {
//       window.nodes.push(node)
//     }
//   })
//   links = window.baseBranches
// }

// // diffing and mutating the data
// function updateData(selectedNode) {
//   var neighbors = getNeighbors(selectedNode)
//   var newNodes = window.baseNodes.filter(function (node) {
//     return neighbors.indexOf(node.id) > -1 || node.level === 1
//   })
//   var diff = {
//     removed: window.nodes.filter(function (node) { return newNodes.indexOf(node) === -1 }),
//     added: newNodes.filter(function (node) { return window.nodes.indexOf(node) === -1 })
//   }
//   diff.removed.forEach(function (node) { window.nodes.splice(window.nodes.indexOf(node), 1) })
//   diff.added.forEach(function (node) { window.nodes.push(node) })
//   links = window.baseBranches.filter(function (link) {
//     return link.target.id === selectedNode.id || link.source.id === selectedNode.id
//   })
// }
// function updateGraph() {
//   // links
//   linkElements = linkGroup.selectAll('line')
//     .data(window.branches, function (link) {
//       return link.target.id + link.source.id
//     })
//   linkElements.exit().remove()
//   var linkEnter = linkElements
//     .enter().append('line')
//     .attr('stroke-width', 1)
//     .attr('stroke', 'rgba(50, 50, 50, 0.2)')
//   linkElements = linkEnter.merge(linkElements)

//   // nodes
//   nodeElements = nodeGroup.selectAll('circle')
//     .data(window.nodes, function (node) { return node.id })
//   nodeElements.exit().remove()
//   var nodeEnter = nodeElements
//     .enter()
//     .append('circle')
//     .attr('r', 10)
//     .attr('fill', function (node) { return node.level === 1 ? 'red' : 'gray' })
//     .call(dragDrop)
//     // we link the selectNode method here
//     // to update the graph on every click
//     .on('click', selectNode)
//   nodeElements = nodeEnter.merge(`nodeElements`)

//   // texts
//   textElements = textGroup.selectAll('text')
//     .data(window.nodes, function (node) { return node.id })
//   textElements.exit().remove()
//   var textEnter = textElements
//     .enter()
//     .append('text')
//     .text(function (node) { return node.url })
//     .attr('font-size', 15)
//     .attr('dx', 15)
//     .attr('dy', 4)
//   textElements = textEnter.merge(textElements)
// }
// function render() {
//   updateGraph()
//   simulation.nodes(window.nodes).on('tick', () => {
//     nodeElements
//       .attr('cx', function (node) { return node.x })
//       .attr('cy', function (node) { return node.y })
//     textElements
//       .attr('x', function (node) { return node.x })
//       .attr('y', function (node) { return node.y })
//     linkElements
//       .attr('x1', function (link) { return link.source.x })
//       .attr('y1', function (link) { return link.source.y })
//       .attr('x2', function (link) { return link.target.x })
//       .attr('y2', function (link) { return link.target.y })
//   })
//   simulation.force('link').links(window.branches)
//   simulation.alphaTarget(0.7).restart()
// }









// var branches = [];
// var nodes = [];
// var WIDTH = window.width;
// var HEIGHT = window.height;

// var svg = d3.select('svg')
// svg.attr('width', width).attr('height', height)

// function renderNode(d) {
//   canvas.fillStyle = 'blue';
//   canvas.beginPath();
//   canvas.fillRect(d.x, d.y, d.r / 2, d.r / 2);
//   canvas.stroke();
//   canvas.fill();
// }

// function renderEdge(e) {
//    console.log(e);

//    canvas.strokeStyle = 'black';
//    canvas.beginPath();
//    canvas.moveTo(e.source.x, e.source.y);
//    canvas.lineTo(e.target.x, e.target.y);
//    canvas.stroke();
//    canvas.fill();

// }

// function renderData(o) {
//    if(o.type === "node") {
//      renderNode(o);
//    } else if(o.type === "link") {
//       renderEdge(o);
//    }
// }

// function FDL(nodesArr, linksArr) {
//     var linkForce = d3
//       .forceLink()
//       .id(function (link) { return link.id })
//       .strength(function (link) { return link.strength })

//     var simulation = d3
//       .forceSimulation()
//       .force('link', linkForce)
//       .force('charge', d3.forceManyBody().strength(-120))
//       .force('center', d3.forceCenter(WIDTH / 2, HEIGHT / 2))

//     simulation.nodes(nodesArr)
//     simulation.force('link').links(linksArr)

//   // var force = d3.force()
//   //         .charge(-40)
//   //         .linkDistance(5)
//   //         .gravity(0.06)
//   //         .size([WIDTH, HEIGHT]);
//   //  force.nodes(nodesArr)
//   //       .links(linksArr);

//    // simulation.start();
//    for(i = 0; i < 10; i++) simulation.tick();
//    simulation.stop();

//     console.log(linksArr, simulation)

//     return nodesArr.concat(linksArr);
// }

// var render = renderQueue(renderData).clear(clear_canvas);






//create somewhere to put the force directed graph
var width = window.innerWidth
var height = window.innerHeight
var svg = d3.select('svg')
svg.attr('width', width).attr('height', height)

var linkElements, nodeElements, textElements;
var parentGroup = svg.append("g").attr("class", "everything");
var linkGroup = parentGroup.append('g').attr('class', 'links')
var nodeGroup = parentGroup.append('g').attr('class', 'nodes')
var textGroup = parentGroup.append('g').attr('class', 'texts')

var radius = 15;

//set up the simulation and add forces
var simulation = d3.forceSimulation();
var link_force =  d3.forceLink()
                    .id(function(d) { return d.id; })
                    .strength(function (link) { return link.strength });

var charge_force = d3.forceManyBody().strength(-120);
var center_force = d3.forceCenter(width / 2, height / 2);

simulation
    .force("charge", charge_force)
    .force("center", center_force)
    .force("link", link_force)

//add drag capabilities
var drag_handler = d3.drag()
    .on("start", drag_start)
    .on("drag", drag_drag)
    .on("end", drag_end);

//add zoom capabilities
var zoom_handler = d3.zoom()
    .on("zoom", zoom_actions);

/** Functions **/

//Drag functions
//d is the node
function drag_start(d) {
 if (!d3.event.active) simulation.alphaTarget(0.3).restart();
    d.fx = d.x;
    d.fy = d.y;
}

//make sure you can't drag the circle outside the box
function drag_drag(d) {
  d.fx = d3.event.x;
  d.fy = d3.event.y;
}

function drag_end(d) {
  if (!d3.event.active) simulation.alphaTarget(0);
  d.fx = null;
  d.fy = null;
}

//Zoom functions
function zoom_actions(){
    parentGroup.attr("transform", d3.event.transform)
}

function node_click(node) {
  if (!d3.event.defaultPrevented) {
    console.log('TODO: FIX NODE TOGGLING')
    // node.filtered = node.filtered  || [];
    // for (let i = window.branches.length; i--;) {
    //     branch = window.branches[i]
    //     if (branch.source.id === node.id) {
    //         node.filtered.push(branch)
    //         window.branches.splice(i, 1)
    //     }
    // }
    // console.log('before update', node.filtered, window.branches)
    // render()
  }
}

function updateGraph() {
    // links
    linkElements = linkGroup.selectAll('line')
        .data(window.branches, function (link) {
            return link.target.id + link.source.id
        })
    linkElements.exit().remove()
        var linkEnter = linkElements
        .enter()
        .append('line')
        .attr('stroke-width', 1)
        .attr('stroke', 'rgba(50, 50, 50, 0.2)')
    linkElements = linkEnter.merge(linkElements)

    // nodes
    nodeElements = nodeGroup.selectAll('circle')
        .data(window.nodes, function (node) {
            return node.id
        })
    nodeElements.exit().remove()
    var nodeEnter = nodeElements
        .enter()
        .append('circle')
        .attr('r', 10)
        .attr('fill', function (node) { return node.level === 1 ? 'red' : 'gray' })
        .on('click', node_click)
        .call(drag_handler)
    nodeElements = nodeEnter.merge(nodeElements)

    // texts
    textElements = textGroup.selectAll('text')
        .data(window.nodes, function (node) {
            return node.id
        })
    textElements.exit().remove()
    var textEnter = textElements
        .enter()
        .append('text')
        .text(function (node) { return node.url })
        .attr('font-size', 15)
        .attr('dx', 15)
        .attr('dy', 4)
        .call(drag_handler)
    textElements = textEnter.merge(textElements)

    svg
        .call(zoom_handler)
        .on("dblclick.zoom", null)
}

function tickActions() {
    //update circle positions each tick of the simulation
   nodeElements
        .attr("cx", function(d) { return d.x; })
        .attr("cy", function(d) { return d.y; });

    //update text positions each tick of the simulation
   textElements
        .attr("x", function(d) { return d.x; })
        .attr("y", function(d) { return d.y; });

    //update link positions
    linkElements
        .attr("x1", function(d) { return d.source.x; })
        .attr("y1", function(d) { return d.source.y; })
        .attr("x2", function(d) { return d.target.x; })
        .attr("y2", function(d) { return d.target.y; });
}

function render() {
    updateGraph()
    simulation.nodes(window.nodes).on("tick", tickActions );
    simulation.force('link').links(window.branches)
    simulation.alphaTarget(0.7).restart()
}




function get_strength(node) {
    switch (node.relationship) {
        case 'replied_to':
            return 0.9
        case 'quoted':
            return 0.2
        case 'link':
            return 0.05
        default:
            return 1
    }
}

function formatForD3 (tree, nodes, branches, parentURLHash) {
    nodes = nodes || []
    branches = branches || []

    let node = Object.assign({}, tree);
    node.id = node['url_hash']
    delete node.branches;

    nodes.push(node)
    if (typeof parentURLHash === 'string') {
        console.log(get_strength(node))
        branches.push({
            'parent_url_hash': parentURLHash,
            'child_url_hash': node.id,
            'source': parentURLHash,
            'target': node.id,
            'id': node.id,
            'relationship': node['relationship'],
            'strength': get_strength(node)
        })
    }

    for (let i = tree.branches.length; i--; ) {
        formatForD3(tree.branches[i], nodes, branches, node.id)
    }

    return {nodes, branches}
}

document.addEventListener("DOMContentLoaded", function() {
    // window.cv = d3.select("body")
    //      .append("canvas")
    //      .attr("width", WIDTH)
    //      .attr("height", HEIGHT);
    // window.canvas = cv.node().getContext("2d");


    socket.on(PAGE_CONTEXT.EVENT_KEYS.TREE_UPDATE, function(tree) {
        console.log(tree)
        // let formattedTree = formatForD3(tree)
        // window.baseNodes = formattedTree.nodes
        // window.baseBranches = formattedTree.branches
        // window.nodes = [...window.baseNodes]
        // window.branches = [...window.baseBranches]
        // window.links = [...window.baseBranches]
        // console.log('formattedTree', formattedTree, window.nodes, window.branches)
        // render()
        // var data = FDL(window.nodes, window.branches);
        // render(data);
    });
});
