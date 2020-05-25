import React from 'react';
import CInP from './cinp';
import { Table, TableHead, TableRow, TableCell } from 'react-toolbox';
import { Link } from 'react-router-dom';


class Network extends React.Component
{
  state = {
      network_list: [],
      network: null
  };

  componentDidMount()
  {
    this.update( this.props );
  }

  componentWillReceiveProps( newProps )
  {
    this.setState( { network_list: [], network: null } );
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
          data.address_block_list = data.address_block_list.map( ( item ) => { return CInP.extractIds( item )[0] } );
          this.setState( { network: data } );
        } );
    }
    else
    {
      props.listGet( props.site )
        .then( ( result ) =>
        {
          var network_list = [];
          for ( var id in result.data )
          {
            var network = result.data[ id ];
            id = CInP.extractIds( id )[0];
            network_list.push( {  id: id,
                              name: network.name,
                              created: network.created,
                              updated: network.updated,
                            } );
          }

          this.setState( { network_list: network_list } );
        } );
    }
  }

  render()
  {
    if( this.props.id !== undefined )
    {
      var network = this.state.network;
      return (
        <div>
          <h3>Network Detail</h3>
          { network !== null &&
            <div>
              <table>
                <thead/>
                <tbody>
                  <tr><th>Site</th><td><Link to={ '/site/' + network.site }>{ network.site }</Link></td></tr>
                  <tr><th>Name</th><td>{ network.name }</td></tr>
                  <tr><th>MTU</th><td>{ network.mtu }</td></tr>
                  <tr><th>Address Blocks</th><td>{ network.address_block_list.map( ( id ) => ( <Link to={ '/addressblock/' + id }>{ id }</Link> ) ) }</td></tr>
                  <tr><th>Created</th><td>{ network.created }</td></tr>
                  <tr><th>Updated</th><td>{ network.updated }</td></tr>
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
          <TableCell>Id</TableCell>
          <TableCell>Name</TableCell>
          <TableCell>Created</TableCell>
          <TableCell>Updated</TableCell>
        </TableHead>
        { this.state.network_list.map( ( item ) => (
          <TableRow key={ item.name } >
            <TableCell><Link to={ '/network/' + item.id }>{ item.id }</Link></TableCell>
            <TableCell>{ item.name }</TableCell>
            <TableCell>{ item.created }</TableCell>
            <TableCell>{ item.updated }</TableCell>
          </TableRow>
        ) ) }
      </Table>
    );

  }
};

export default Network;
