import React from 'react';
import { Dialog, Table, TableHead, TableRow, TableCell, Button } from 'react-toolbox';

class ConfigDialog extends React.Component
{
  state = {
      active: false,
      item_list: [],
  };

  show = () =>
  {
    this.props.getConfig( this.props.uri )
    .then( ( result ) =>
      {
        var item_list = [];

        for( var name in result.data )
        {
          item_list.push( { name: name, value: result.data[ name ] } );
        }
        this.setState( { active: true, item_list: item_list } );
      } );
  };

  close = () =>
  {
    this.setState( { active: false } );
  };

  actions = [
    { label: "Close", onClick: this.close },
  ];

  render()
  {
    return (
      <div>
        <Dialog
          actions={this.actions}
          active={this.state.active}
          onEscKeyDown={this.close}
          onOverlayClick={this.close}
          title='Full Config'
        >
          <Table selectable={ false } multiSelectable={ false }>
            <TableHead>
              <TableCell>Name</TableCell>
              <TableCell>Value</TableCell>
            </TableHead>
          { this.state.item_list.map( ( item ) => (
            <TableRow key={ item.name }>
              <TableCell>{ item.name }</TableCell>
              <TableCell>{ item.value }</TableCell>
            </TableRow>
          ) ) }
          </Table>
        </Dialog>
        <Button onClick={ this.show }>Display Full Config</Button>
      </div>
);
  }
};

export default ConfigDialog;
