import React from 'react';
import { Dialog } from 'react-toolbox';

class ServerError extends React.Component
{
  state = {
      active: false,
      msg: '',
      trace: '',
  };

  show = ( msg, trace ) =>
  {
    if( trace === undefined )
    {
      trace = '';
    }
    this.setState( { active: true, msg: msg, trace: trace } )
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
  <Dialog
    actions={this.actions}
    active={this.state.active}
    onEscKeyDown={this.close}
    onOverlayClick={this.close}
    title='Server Error'
  >
    <p>{this.state.msg}</p>
    <pre>{this.state.trace}</pre>
  </Dialog>
);
  }
}

export default ServerError;
