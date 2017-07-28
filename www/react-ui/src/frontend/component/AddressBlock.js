import React from 'react';
import CInP from './cinp';
import { Table, TableHead, TableRow, TableCell } from 'react-toolbox';
import { Link } from 'react-router-dom';


class AddressBlock extends React.Component
{
  state = {
      addressBlock_list: [],
      addressBlock: null,
      addressBlockAddress_list: []
  };

  componentDidMount()
  {
    this.update( this.props );
  }

  componentWillReceiveProps( newProps )
  {
    this.setState( { addressBlock_list: [], addressBlock: null } );
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
          this.setState( { addressBlock: data } );
        } );

      props.addressListGetter( props.id )
        .then( ( result ) =>
        {
          var addressBlockAddress_list = [];
          for( var id in result )
          {
            var address = result[ id ];
            addressBlockAddress_list.push( { id: id,
                                             type: address.type,
                                             ip_address: address.ip_address,
                                             offset: address.offset,
                                             reason: address.reason, // ReservedAddress
                                             networked: address.networked, // Address
                                             created: address.created,
                                             updated: address.updated
                                           } );
          }
          this.setState( { addressBlockAddress_list: addressBlockAddress_list } );
        } );
    }
    else
    {
      props.listGet( props.site )
        .then( ( result ) =>
        {
          var addressBlock_list = [];
          for ( var id in result.data )
          {
            var addressBlock = result.data[ id ];
            id = CInP.extractIds( id )[0];
            addressBlock_list.push( { id: id,
                                    subnet: addressBlock.subnet,
                                    prefix: addressBlock.prefix,
                                    created: addressBlock.created,
                                    updated: addressBlock.updated
                                  } );
          }

          this.setState( { addressBlock_list: addressBlock_list } );
        } );
    }
  }

  render()
  {
    if( this.props.id !== undefined )
    {
      var addressBlock = this.state.addressBlock;
      return (
        <div>
          <h3>Address Block Detail</h3>
          { addressBlock !== null &&
            <div>
              <table>
                <thead/>
                <tbody>
                  <tr><th>Site</th><td><Link to={ '/site/' + addressBlock.site }>{ addressBlock.site }</Link></td></tr>
                  <tr><th>Subnet</th><td>{ addressBlock.subnet }</td></tr>
                  <tr><th>Prefix</th><td>{ addressBlock.prefix }</td></tr>
                  <tr><th>Gateway</th><td>{ addressBlock.gateway }</td></tr>
                  <tr><th>Max Address</th><td>{ addressBlock._max_address }</td></tr>
                  <tr><th>Created</th><td>{ addressBlock.created }</td></tr>
                  <tr><th>Updated</th><td>{ addressBlock.updated }</td></tr>
                </tbody>
              </table>
              <h3>Address List</h3>
              <Table selectable={ false } multiSelectable={ false }>
                <TableHead>
                  <TableCell numeric>Id</TableCell>
                  <TableCell>Type</TableCell>
                  <TableCell>Ip Address</TableCell>
                  <TableCell>Offset</TableCell>
                  <TableCell>Reason/Networked</TableCell>
                  <TableCell>Created</TableCell>
                  <TableCell>Updated</TableCell>
                </TableHead>
                { this.state.addressBlockAddress_list.map( ( item ) => (
                  <TableRow key={ item.id }>
                    <TableCell numeric>{ item.id }</TableCell>
                    <TableCell>{ item.type }</TableCell>
                    <TableCell>{ item.ip_address }</TableCell>
                    <TableCell>{ item.offset }</TableCell>
                    <TableCell>{ item.reason } { item.networked }</TableCell>
                    <TableCell>{ item.created }</TableCell>
                    <TableCell>{ item.updated }</TableCell>
                  </TableRow>
                ) ) }
              </Table>
            </div>
          }
        </div>
      );
    }

    return (
      <Table selectable={ false } multiSelectable={ false }>
        <TableHead>
          <TableCell numeric>Id</TableCell>
          <TableCell>Subnet</TableCell>
          <TableCell>Prefix</TableCell>
          <TableCell>Created</TableCell>
          <TableCell>Updated</TableCell>
        </TableHead>
        { this.state.addressBlock_list.map( ( item ) => (
          <TableRow key={ item.id }>
            <TableCell numeric><Link to={ '/addressblock/' + item.id }>{ item.id }</Link></TableCell>
            <TableCell>{ item.subnet }</TableCell>
            <TableCell>{ item.prefix }</TableCell>
            <TableCell>{ item.created }</TableCell>
            <TableCell>{ item.updated }</TableCell>
          </TableRow>
        ) ) }
      </Table>
    );

  }
};

export default AddressBlock;
