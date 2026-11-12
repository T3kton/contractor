import React from 'react';
import { Box, Button, Dialog, DialogActions, DialogContent, DialogTitle, Table, TableBody, TableCell, TableHead, TableRow, Typography } from '@mui/material';

interface JobStateDialogProps {
  getState: ( uri: string ) => Promise<any>;
  uri: string;
}

interface VariableItem {
  name: string;
  value: string;
}

interface JobStateDialogState {
  active: boolean;
  variable_list: VariableItem[];
  cur_line?: number;
  stack?: string;
  script?: string;
}

class JobStateDialog extends React.Component<JobStateDialogProps, JobStateDialogState>
{
  state: JobStateDialogState = {
      active: false,
      variable_list: [],
  };

  show = () =>
  {
    this.props.getState( this.props.uri )
    .then( ( result: any ) =>
      {
        var variable_list: VariableItem[] = [];
        const vars = result[0]?.data !== undefined ? result[0].data : result[0];
        for( var name in vars )
        {
          variable_list.push( { name: name, value: JSON.stringify( vars[ name ] ) } );
        }
        var state = result[1]?.data !== undefined ? result[1].data : result[1];
        this.setState( { active: true, variable_list: variable_list, cur_line: state.cur_line, stack: JSON.stringify( state.state ), script: state.script } );
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
        <Dialog open={ this.state.active } onClose={ this.close }>
          <DialogTitle>Job State</DialogTitle>
          <DialogContent>
            <Box>
              <Table size="small">
                <TableBody>
                  { ( this.state.script ?? '' ).split( /[\r\n]/ ).map( ( line, index ) => (
                    <TableRow key={ index } selected={ index === this.state.cur_line }>
                      <TableCell sx={{ py: 0 }}>{ index }</TableCell>
                      <TableCell sx={{ py: 0 }}><pre style={{ margin: 0 }}>{ line }</pre></TableCell>
                    </TableRow>
                  ) ) }
                </TableBody>
              </Table>
              <Typography>on line: <strong>{ this.state.cur_line }</strong></Typography>
              <Table size="small">
                <TableHead>
                  <TableRow>
                    <TableCell>Name</TableCell>
                    <TableCell>Value</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  { this.state.variable_list.map( ( item, index ) => (
                    <TableRow key={ index }>
                      <TableCell>{ item.name }</TableCell>
                      <TableCell>{ item.value }</TableCell>
                    </TableRow>
                  ) ) }
                </TableBody>
              </Table>
              <Typography>{ this.state.stack }</Typography>
            </Box>
          </DialogContent>
          <DialogActions>
            <Button onClick={ this.close }>Close</Button>
          </DialogActions>
        </Dialog>
        <Button onClick={ this.show }>Display Internal Job Info</Button>
      </Box>
);
  }
};

export default JobStateDialog;
