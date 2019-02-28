import React from 'react';
import CInP from './cinp';
import { Table, TableHead, TableRow, TableCell } from 'react-toolbox';
import { Link } from 'react-router-dom';


class Dependency extends React.Component
{
  state = {
      dependency_list: [],
      dependency: null,
  };

  componentDidMount()
  {
    this.update( this.props );
  }

  componentWillReceiveProps( newProps )
  {
    this.setState( { dependency_list: [], dependency: null } );
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
          data.dependency = CInP.extractIds( data.dependency )[0];
          data.foundation = CInP.extractIds( data.foundation )[0];
          data.script_structure = CInP.extractIds( data.script_structure )[0];
          this.setState( { dependency: data } );
        } );
    }
    else
    {
      props.listGet( props.site )
        .then( ( result ) =>
        {
          var dependency_list = [];
          for ( var id in result.data )
          {
            var dependency = result.data[ id ];
            id = CInP.extractIds( id )[0];
            dependency_list.push( { id: id,
                                    foundation: dependency.foundation,
                                    structure: dependency.structure,
                                    script_name: dependency.script_name,
                                    state: dependency.state,
                                    created: dependency.created,
                                    updated: dependency.updated,
                                  } );
          }

          this.setState( { dependency_list: dependency_list } );
        } );
    }
  }

  render()
  {
    if( this.props.id !== undefined )
    {
      var dependency = this.state.dependency;
      return (
        <div>
          <h3>Dependency Detail</h3>
          { dependency !== null &&
            <table>
              <thead/>
              <tbody>
                <tr><th>Structure</th><td><Link to={ '/structure/' + dependency.structure }>{ dependency.structure }</Link></td></tr>
                <tr><th>Dependency</th><td><Link to={ '/dependency/' + dependency.dependency }>{ dependency.dependency }</Link></td></tr>
                <tr><th>Foundation</th><td><Link to={ '/foundation/' + dependency.foundation }>{ dependency.foundation }</Link></td></tr>
                <tr><th>Script Structure</th><td><Link to={ '/structure/' + dependency.script_structure }>{ dependency.script_structure }</Link></td></tr>
                <tr><th>Create Script Name</th><td>{ dependency.create_script_name }</td></tr>
                <tr><th>Destroy Script Name</th><td>{ dependency.destroy_script_name }</td></tr>
                <tr><th>State</th><td>{ dependency.state }</td></tr>
                <tr><th>Link</th><td>{ dependency.link }</td></tr>
                <tr><th>Created</th><td>{ dependency.created }</td></tr>
                <tr><th>Updated</th><td>{ dependency.updated }</td></tr>
                <tr><th>Built At</th><td>{ dependency.built_at }</td></tr>
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
        { this.state.dependency_list.map( ( item ) => (
          <TableRow key={ item.id }>
            <TableCell numeric><Link to={ '/dependency/' + item.id }>{ item.id }</Link></TableCell>
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

export default Dependency;
