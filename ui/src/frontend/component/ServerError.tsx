import React from 'react';
import { useSelector, useDispatch } from 'react-redux';
import { Button, Dialog, DialogActions, DialogContent, DialogTitle } from '@mui/material';
import type { RootState, AppDispatch } from '../store';
import { clearServerError } from '../store/appSlice';

const ServerError: React.FC = () =>
{
  const dispatch = useDispatch<AppDispatch>();
  const serverError = useSelector( ( s: RootState ) => s.app.serverError );

  return (
    <Dialog open={ serverError !== null } onClose={ () => dispatch( clearServerError() ) } maxWidth="lg">
      <DialogTitle>Server Error</DialogTitle>
      <DialogContent>
        <p>{ serverError?.msg }</p>
        <pre>{ serverError?.trace }</pre>
      </DialogContent>
      <DialogActions>
        <Button onClick={ () => dispatch( clearServerError() ) }>Close</Button>
      </DialogActions>
    </Dialog>
  );
};

export default ServerError;
