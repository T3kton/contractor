import React from 'react';
import CInP from './cinp';
import ConfigDialog from './ConfigDialog';
import { Table, TableHead, TableRow, TableCell } from 'react-toolbox';
import { Link } from 'react-router-dom';


class PXE extends React.Component
{
  state = {
      pxe_list: [],
      pxe: null
  };

  componentDidMount()
  {
    this.update( this.props );
  }

  componentWillReceiveProps( newProps )
  {
    this.setState( { pxe_list: [], pxe: null } );
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
          this.setState( { pxe: data } );
        } );
    }
    else
    {
      props.listGet()
        .then( ( result ) =>
        {
          var pxe_list = [];
          for ( var name in result.data )
          {
            var pxe = result.data[ name ];
            name = CInP.extractIds( name )[0];
            pxe_list.push( { name: name,
                              created: pxe.created,
                              updated: pxe.updated,
                            } );
          }

          this.setState( { pxe_list: pxe_list } );
        } );
    }
  }

  render()
  {
    if( this.props.id !== undefined )
    {
      var pxe = this.state.pxe;
      return (
        <div>
          <h3>PXE Detail</h3>
          { pxe !== null &&
            <div>
              <table>
                <thead/>
                <tbody>
                  <tr><th>Name</th><td>{ pxe.name }</td></tr>
                  <tr><th>Boot Script</th><td><pre>{ pxe.boot_script }</pre></td></tr>
                  <tr><th>Template</th><td><pre>{ pxe.template }</pre></td></tr>
                  <tr><th>Created</th><td>{ pxe.created }</td></tr>
                  <tr><th>Updated</th><td>{ pxe.updated }</td></tr>
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
        { this.state.pxe_list.map( ( item ) => (
          <TableRow key={ item.name } >
            <TableCell><Link to={ '/pxe/' + item.name }>{ item.name }</Link></TableCell>
            <TableCell>{ item.created }</TableCell>
            <TableCell>{ item.updated }</TableCell>
          </TableRow>
        ) ) }
      </Table>
    );

  }
};

export default PXE;
