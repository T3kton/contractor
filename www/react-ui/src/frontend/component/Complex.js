import React from 'react';
import CInP from './cinp';
import { Table, TableHead, TableRow, TableCell } from 'react-toolbox';
import { Link } from 'react-router-dom';


class Complex extends React.Component
{
  state = {
      complex_list: [],
      complex: null
  };

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
    if( props.id !== undefined )
    {
      props.detailGet( props.id )
       .then( ( result ) =>
        {
          var data = result.data;
          data.site = CInP.extractIds( data.site )[0];
          this.setState( { complex: data } );
        } );
    }
    else
    {
      props.listGet( props.site )
        .then( ( result ) =>
        {
          var complex_list = [];
          for ( var id in result.data )
          {
            var complex = result.data[ id ];
            id = CInP.extractIds( id )[0];
            complex_list.push( { id: id,
                                    description: complex.description,
                                    type: complex.type,
                                    state: complex.state,
                                    created: complex.created,
                                    updated: complex.updated,
                                  } );
          }

          this.setState( { complex_list: complex_list } );
        } );
    }
  }

  render()
  {
    if( this.props.id !== undefined )
    {
      var complex = this.state.complex;
      return (
        <div>
          <h3>Complex Detail</h3>
          { complex !== null &&
            <table>
              <thead/>
              <tbody>
                <tr><th>Site</th><td><Link to={ '/site/' + complex.site }>{ complex.site }</Link></td></tr>
                <tr><th>Description</th><td>{ complex.description }</td></tr>
                <tr><th>Name</th><td>{ complex.name }</td></tr>
                <tr><th>State</th><td>{ complex.state }</td></tr>
                <tr><th>Type</th><td>{ complex.type }</td></tr>
                <tr><th>Members</th><td>{ complex.members }</td></tr>
                <tr><th>Built at Percentage</th><td>{ complex.built_percentage }%</td></tr>
                <tr><th>Created</th><td>{ complex.created }</td></tr>
                <tr><th>Updated</th><td>{ complex.updated }</td></tr>
              </tbody>
            </table>
          }
        </div>
      );
    }

    return (
      <Table selectable={ false } multiSelectable={ false }>
        <TableHead>
          <TableCell numeric>Id</TableCell>
          <TableCell>Description</TableCell>
          <TableCell>Type</TableCell>
          <TableCell>State</TableCell>
          <TableCell>Created</TableCell>
          <TableCell>Updated</TableCell>
        </TableHead>
        { this.state.complex_list.map( ( item ) => (
          <TableRow>
            <TableCell numeric><Link to={ '/complex/' + item.id }>{ item.id }</Link></TableCell>
            <TableCell>{ item.hostname }</TableCell>
            <TableCell>{ item.state }</TableCell>
            <TableCell>{ item.created }</TableCell>
            <TableCell>{ item.updated }</TableCell>
          </TableRow>
        ) ) }
      </Table>
    );

  }
};

export default Complex;
