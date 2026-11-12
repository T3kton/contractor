import React from 'react';
import { Box, Button, Dialog, DialogActions, DialogContent, DialogTitle, Table, TableBody, TableCell, TableRow } from '@mui/material';

interface ScriptDialogProps {
  getScript: ( id: string ) => Promise<any>;
  id: string;
}

interface ScriptData {
  name: string;
  description: string;
  script: string;
}

interface ScriptDialogState {
  active: boolean;
  script: ScriptData;
}

class ScriptDialog extends React.Component<ScriptDialogProps, ScriptDialogState>
{
  state: ScriptDialogState = {
      active: false,
      script: { name: '', description: '', script: '' },
  };

  show = () =>
  {
    this.props.getScript( this.props.id )
    .then( ( result: any ) =>
      {
        const data = result?.data !== undefined ? result.data : result;
        var script: ScriptData = {
          name: data.name ?? '',
          description: data.description ?? '',
          script: data.script ?? '',
        };

        this.setState( { active: true, script: script } );
      } );
  };

  close = () =>
  {
    this.setState( { active: false } );
  };

  render()
  {
    return (
      <Box>
        <Dialog open={ this.state.active } onClose={ this.close } maxWidth="lg">
          <DialogTitle>Script</DialogTitle>
          <DialogContent>
            <Table size="small">
              <TableBody>
                <TableRow><TableCell variant="head">Name</TableCell><TableCell>{ this.state.script.name }</TableCell></TableRow>
                <TableRow><TableCell variant="head">Description</TableCell><TableCell>{ this.state.script.description }</TableCell></TableRow>
              </TableBody>
            </Table>
            <pre>{ this.state.script.script }</pre>
          </DialogContent>
          <DialogActions>
            <Button onClick={ this.close }>Close</Button>
          </DialogActions>
        </Dialog>
        <Button onClick={ this.show }>Display</Button>
      </Box>
);
  }
};

export default ScriptDialog;
