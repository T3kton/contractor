import React from 'react';
import CInP from './cinp';
import Graph from 'react-graph-vis';

const stateColorMap = { 'planned': '#88FF88', 'located': '#8888FF', 'built': '#000000' };

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
        blockShifting: true,
        sortMethod: 'directed'
      },
      improvedLayout: true
    },
    edges: {
      color: "#000000",
      arrows: 'to'
    },
    groups: {
      Structure: {
        physics: false,
        shape: 'icon',
        icon: {
          face: 'Material Icons',
          code: '\ue84f',
          size: 50
        }
      },
      Foundation: {
        physics: false,
        shape: 'icon',
        icon: {
          face: 'Material Icons',
          code: '\ue1db',
          size: 50
        }
      },
      Complex: {
        physics: false,
        shape: 'icon',
        icon: {
          face: 'Material Icons',
          code: '\ue7f1',
          size: 50
        }
      },
      Dependancy: {
        physics: false,
        shape: 'icon',
        icon: {
          face: 'Material Icons',
          code: '\ue886',
          size: 50
        }
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
          var shadow = { enabled: false };
          if ( node.external || node.has_job )
          {
            shadow.enabled = true;
            shadow.x = 10;
            shadow.y = 10;
            shadow.size = 4;
            if ( node.external )
            {
              shadow.color = '#DDDDDD';
            }
            else
            {
              shadow.color = '#FF0000';
            }
          }
          graph.nodes.push( { id: id, label: node.description, icon: { color: stateColorMap[ node.state ] }, group: node.type, shadow: shadow } );
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
    let style = { width:"100%", height:"1000px" };
    return (<Graph graph={ this.state.graph } options={ this.graph_options } events={ this.graph_events } style={ style }/>);
  }
}

export default SiteGraph;
