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
    layout: {
      hierarchical: true
    },
    edges: {
      height: "100%",
      color: "#000000",
      edges:{
        arrows: 'to',
      }
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
    return (<Graph graph={ this.state.graph } options={ this.graph_options } events={ this.graph_events } />)
  }
}

export default SiteGraph;
