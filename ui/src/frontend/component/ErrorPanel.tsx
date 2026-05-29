import React from 'react';
import { Alert, Button } from '@mui/material';

interface Props {
  error: string;
  onRetry?: () => void;
}

const ErrorPanel: React.FC<Props> = ( { error, onRetry } ) => (
  <Alert
    severity="error"
    action={
      onRetry && (
        <Button color="inherit" size="small" onClick={ onRetry }>
          Retry
        </Button>
      )
    }
  >
    { error }
  </Alert>
);

export default ErrorPanel;
