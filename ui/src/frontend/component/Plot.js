import React from 'react';
import CInP from './cinp';
import { Table, TableHead, TableRow, TableCell } from 'react-toolbox';
import { Link } from 'react-router-dom';


class Plot extends React.Component
{
  state = {
      plot_list: [],
      plot: null
  };

  componentDidMount()
  {
    this.update( this.props );
  }

  componentWillReceiveProps( newProps )
  {
    this.setState( { plot_list: [], plot: null } );
    this.update( newProps );
  }

  update( props )
  {
    if( props.id !== undefined )
    {
      props.detailGet( props.id )
       .then( ( result ) =>
        {
          var data = result.data;
          data.parent = CInP.extractIds( data.parent )[0];
          this.setState( { plot: data } );
        } );
    }
    else
    {
      props.listGet()
        .then( ( result ) =>
        {
          var plot_list = [];
          for ( var name in result.data )
          {
            var plot = result.data[ name ];
            name = CInP.extractIds( name )[0];
            plot_list.push( { name: name,
                              created: plot.created,
                              updated: plot.updated,
                            } );
          }

          this.setState( { plot_list: plot_list } );
        } );
    }
  }

  render()
  {
    if( this.props.id !== undefined )
    {
      var plot = this.state.plot;
      return (
        <div>
          <h3>Plot Detail</h3>
          { plot !== null &&
            <div>
              <table>
                <thead/>
                <tbody>
                  <tr><th>Name</th><td>{ plot.name }</td></tr>
                  <tr><th>Parent</th><td><Link to={ '/plot/' + plot.parent }>{ plot.parent }</Link></td></tr>
                  <tr><th>Corners</th><td>{ plot.corners }</td></tr>
                  <tr><th>Created</th><td>{ plot.created }</td></tr>
                  <tr><th>Updated</th><td>{ plot.updated }</td></tr>
                </tbody>
              </table>
            </div>
          }
        </div>
      );
    }

    return (
      <Table selectable={ false } multiSelectable={ false }>
        <TableHead>
          <TableCell>Name</TableCell>
          <TableCell>Created</TableCell>
          <TableCell>Updated</TableCell>
        </TableHead>
        { this.state.plot_list.map( ( item ) => (
          <TableRow key={ item.name } >
            <TableCell><Link to={ '/plot/' + item.name }>{ item.name }</Link></TableCell>
            <TableCell>{ item.created }</TableCell>
            <TableCell>{ item.updated }</TableCell>
          </TableRow>
        ) ) }
      </Table>
    );

  }
};

export default Plot;
