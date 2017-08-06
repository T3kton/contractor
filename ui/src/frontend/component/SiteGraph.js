import React from 'react';
import CInP from './cinp';
import Graph from 'react-graph-vis';

const stateColorMap = { 'planned': '#88FF88', 'located': '#8888FF', 'built': '#FFFFFF' };
const typeShapeMap = { 'Structure': 'ellipse', 'Foundation': 'box', 'Complex': 'database', 'Dependancy': 'diamond' };

class SiteGraph extends React.Component
{
  state = {
    graph: { nodes: {}, edges: {} }
  };

  graph_options = {
    height: "100%",
    width: "100%",
    layout: {
      hierarchical: {
        enabled: true,
        //edgeMinimization: true,
        //blockShifting: true,
        improvedLayout: true,
        sortMethod: 'directed'
      }
    },
    edges: {
      color: "#000000",
      arrows: 'to'
    }
  };

  graph_events = {};

  componentDidMount()
  {
    this.update( this.props );
  }

  componentWillReceiveProps( newProps )
  {
    this.setState( { complex_list: [], complex: null } );
    this.update( newProps );
  }

  update( props )
  {
    props.siteDependancyMap( props.site )
      .then( ( result ) =>
      {
        var graph = { nodes: [], edges: [] };
        for ( var id in result.data )
        {
          var node = result.data[ id ];
          var border_color = '#000000';
          if ( node.external )
          {
            border_color = '#2B7CE9';
          }
          graph.nodes.push( { id: id, label: node.description, color: { border: border_color, background: stateColorMap[ node.state ] }, shape: typeShapeMap[ node.type ] } );
          for ( var i in node.dependancy_list )
          {
            graph.edges.push( { from: node.dependancy_list[ i ], to: id } );
          }
        }

        this.setState( { graph: graph } );
      } );
  }

  render()
  {
    let style = { width:"100%", height:"600px" };
    return (<Graph graph={ this.state.graph } options={ this.graph_options } events={ this.graph_events } style={ style }/>);
  }
}

export default SiteGraph;
