import React from 'react';
import { Dialog, Table, TableHead, TableRow, TableCell, Button } from 'react-toolbox';
import theme from './ScriptDialogTheme.css';

class ScriptDialog extends React.Component
{
  state = {
      active: false,
      script: { name: '', description: '', script_lines: [] },
  };

  show = () =>
  {
    this.props.getScript( this.props.id )
    .then( ( result ) =>
      {
        var script = {};

        script.name = result.data.name;
        script.description = result.data.description;
        script.script_lines = result.data.script.split( /[\r\n]/ );

        this.setState( { active: true, script: script } );
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
          title='Script'
          theme={ theme }
        >
          <table>
            <thead/>
            <tbody>
              <tr><th>Name</th><td>{ this.state.script.name }</td></tr>
              <tr><th>Description</th><td>{ this.state.script.description }</td></tr>
            { this.state.script.script_lines.map( ( item, index ) => (
              <tr key={ index }><td>{ index }</td><td>{ item }</td></tr>
            ) ) }
            </tbody>
          </table>
        </Dialog>
        <Button onClick={ this.show }>Display</Button>
      </div>
);
  }
};

export default ScriptDialog;
