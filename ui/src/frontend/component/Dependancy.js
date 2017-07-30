import React from 'react';
import CInP from './cinp';
import { Table, TableHead, TableRow, TableCell } from 'react-toolbox';
import { Link } from 'react-router-dom';


class Dependancy extends React.Component
{
  state = {
      dependancy_list: [],
      dependancy: null,
  };

  componentDidMount()
  {
    this.update( this.props );
  }

  componentWillReceiveProps( newProps )
  {
    this.setState( { dependancy_list: [], dependancy: null } );
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
          data.structure = CInP.extractIds( data.structure )[0];
          data.foundation = CInP.extractIds( data.foundation )[0];
          this.setState( { dependancy: data } );
        } );
    }
    else
    {
      props.listGet( props.site )
        .then( ( result ) =>
        {
          var dependancy_list = [];
          for ( var id in result.data )
          {
            var dependancy = result.data[ id ];
            id = CInP.extractIds( id )[0];
            dependancy_list.push( { id: id,
                                    foundation: dependancy.foundation,
                                    structure: dependancy.structure,
                                    script_name: dependancy.script_name,
                                    state: dependancy.state,
                                    created: dependancy.created,
                                    updated: dependancy.updated,
                                  } );
          }

          this.setState( { dependancy_list: dependancy_list } );
        } );
    }
  }

  render()
  {
    if( this.props.id !== undefined )
    {
      var dependancy = this.state.dependancy;
      return (
        <div>
          <h3>Dependancy Detail</h3>
          { dependancy !== null &&
            <table>
              <thead/>
              <tbody>
                <tr><th>Foundation</th><td><Link to={ '/foundation/' + dependancy.foundation }>{ dependancy.foundation }</Link></td></tr>
                <tr><th>Structure</th><td><Link to={ '/structure/' + dependancy.structure }>{ dependancy.structure }</Link></td></tr>
                <tr><th>Script Name</th><td>{ dependancy.script_name }</td></tr>
                <tr><th>State</th><td>{ dependancy.state }</td></tr>
                <tr><th>Link</th><td>{ dependancy.link }</td></tr>
                <tr><th>Created</th><td>{ dependancy.created }</td></tr>
                <tr><th>Updated</th><td>{ dependancy.updated }</td></tr>
                <tr><th>Built At</th><td>{ dependancy.built_at }</td></tr>
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
          <TableCell>Foundation</TableCell>
          <TableCell>Structure</TableCell>
          <TableCell>State</TableCell>
          <TableCell>Created</TableCell>
          <TableCell>Updated</TableCell>
        </TableHead>
        { this.state.dependancy_list.map( ( item ) => (
          <TableRow key={ item.id }>
            <TableCell numeric><Link to={ '/dependancy/' + item.id }>{ item.id }</Link></TableCell>
            <TableCell>{ item.foundation }</TableCell>
            <TableCell>{ item.structure }</TableCell>
            <TableCell>{ item.state }</TableCell>
            <TableCell>{ item.created }</TableCell>
            <TableCell>{ item.updated }</TableCell>
          </TableRow>
        ) ) }
      </Table>
    );

  }
};

export default Dependancy;
