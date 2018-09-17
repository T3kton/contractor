import React from 'react';
import { Dialog, Table, TableHead, TableRow, TableCell, Button } from 'react-toolbox';
import theme from './JobStateDialogTheme.css';

class JobStateDialog extends React.Component
{
  state = {
      active: false,
      variable_list: [],
  };

  show = () =>
  {
    this.props.getState( this.props.uri )
    .then( ( result ) =>
      {
        var variable_list = [];

        for( var name in result[0].data )
        {
          variable_list.push( { name: name, value: JSON.stringify( result[0].data[ name ] ) } );
        }

        var state = result[1].data;

        this.setState( { active: true, variable_list: variable_list, cur_line: state.cur_line, stack: state.state, script: state.script } );
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
          actions={ this.actions }
          active={ this.state.active }
          onEscKeyDown={ this.close }
          onOverlayClick={ this.close }
          title='Job State'
          theme={ theme }
        >
          <div>
            <pre>{ this.state.script }</pre>
            <p>on line: <strong>{ this.state.cur_line }</strong></p>
            <Table selectable={ false } multiSelectable={ false }>
              <TableHead>
                <TableCell>Name</TableCell>
                <TableCell>Value</TableCell>
              </TableHead>
            { this.state.variable_list.map( ( item, index ) => (
              <TableRow key={ index }>
                <TableCell>{ item.name }</TableCell>
                <TableCell>{ item.value }</TableCell>
              </TableRow>
            ) ) }
            </Table>
            <p>{ this.state.stack }</p>
          </div>
        </Dialog>
        <Button onClick={ this.show }>Display Internal Job Info</Button>
      </div>
);
  }
};

export default JobStateDialog;
