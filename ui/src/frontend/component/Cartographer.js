import React from 'react';
import CInP from './cinp';
import { Table, TableHead, TableRow, TableCell } from 'react-toolbox';
import { Link } from 'react-router-dom';

class Cartographer extends React.Component
{
  state = {
      cartographer_list: []
  };

  componentDidMount()
  {
    this.update( this.props );
  }

  componentWillReceiveProps( newProps )
  {
    this.setState( { cartographer_list: [] } );
    this.update( newProps );
  }

  update( props )
  {
    props.listGet()
      .then( ( result ) =>
      {
        var cartographer_list = [];
        for ( var id in result.data )
        {
          var cartographer = result.data[ id ];
          id = CInP.extractIds( id )[0];
          cartographer_list.push( { id: id,
                            identifier: cartographer.identifier,
                            message: cartographer.message,
                            foundation: CInP.extractIds( cartographer.foundation )[0],
                            created: cartographer.created,
                            updated: cartographer.updated
                          } );
        }

        this.setState( { cartographer_list: cartographer_list } );
      } );
  }

  render()
  {
    return (
      <Table selectable={ false } multiSelectable={ false }>
        <TableHead>
          <TableCell>Identifier</TableCell>
          <TableCell>Message</TableCell>
          <TableCell>Foundation</TableCell>
          <TableCell>Created</TableCell>
          <TableCell>Updated</TableCell>
        </TableHead>
        { this.state.cartographer_list.map( ( item ) => (
          <TableRow key={ item.id } >
            <TableCell>{ item.identifier }</TableCell>
            <TableCell>{ item.message }</TableCell>
            <TableCell><Link to={ '/plot/' + item.foundation }>{ item.foundation }</Link></TableCell>
            <TableCell>{ item.created }</TableCell>
            <TableCell>{ item.updated }</TableCell>
          </TableRow>
        ) ) }
      </Table>
    );

  }
};

export default Cartographer;
