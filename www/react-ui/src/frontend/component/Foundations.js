import React from 'react';
import CInP from './cinp';
import { Table, TableHead, TableRow, TableCell } from 'react-toolbox';
import { Link } from 'react-router-dom';
import createFragment from 'react-addons-create-fragment';


class Foundations extends React.Component
{
  state = {
      foundation_list: [],
      foundation: null
  };

  componentDidMount()
  {
    if( this.props.uid !== undefined )
    {
      this.props.foundationGet( this.props.uid )
       .then( ( result ) =>
        {
          this.setState( { foundation: result.data } );
        } );
    }
    else
    {
      this.props.foundationListGetter( this.props.site )
        .then( ( result ) =>
        {
          var foundation_list = [];
          for ( var id in result.data )
          {
            var foundation = result.data[ id ];
            id = CInP.extractIds( id )[0];
            foundation_list.push( { id: id,
                                    locator: foundation.locator,
                                    state: foundation.state,
                                    created: foundation.created,
                                    updated: foundation.updated,
                                  } );
          }

          this.setState( { foundation_list: foundation_list } );
        } );
    }
  }

  render()
  {
    if( this.props.uid !== undefined )
    {
      return (
        <div>
          <h1>Foundation Detail</h1>
          { this.state.foundation !== null &&
            <table>
              <thead/>
              <tbody>
                <tr><th>Site</th><td>{ this.state.foundation.site }</td></tr>
                <tr><th>Locator</th><td>{ this.state.foundation.locator }</td></tr>
                <tr><th>State</th><td>{ this.state.foundation.state }</td></tr>
                <tr><th>Type</th><td>{ this.state.foundation.type }</td></tr>
                <tr><th>Blueprint</th><td>{ this.state.foundation.blueprint }</td></tr>
                <tr><th>Id Map</th><td>{ this.state.foundation.id_map }</td></tr>
                <tr><th>Interfaces</th><td>{ this.state.foundation.interfaces }</td></tr>
                <tr><th>Class List</th><td>{ this.state.foundation.class_list }</td></tr>
                <tr><th>Config Values</th><td>{ createFragment( this.state.foundation.config_values ) }</td></tr>
                <tr><th>Created</th><td>{ this.state.foundation.created }</td></tr>
                <tr><th>Updated</th><td>{ this.state.foundation.updated }</td></tr>
                <tr><th>Located At</th><td>{ this.state.foundation.located_at }</td></tr>
                <tr><th>Built At</th><td>{ this.state.foundation.built_at }</td></tr>
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
          <TableCell>Locator</TableCell>
          <TableCell>State</TableCell>
          <TableCell>Created</TableCell>
          <TableCell>Updated</TableCell>
        </TableHead>
        { this.state.foundation_list.map( ( item, uri ) => (
          <TableRow key={ uri }>
            <TableCell numeric><Link to={ '/foundations/' + item.id }>{ item.id }</Link></TableCell>
            <TableCell>{ item.locator }</TableCell>
            <TableCell>{ item.state }</TableCell>
            <TableCell>{ item.created }</TableCell>
            <TableCell>{ item.updated }</TableCell>
          </TableRow>
        ) ) }
      </Table>
    );

  }
};

export default Foundations;
