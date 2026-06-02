import React from 'react';
import { createTheme, ThemeProvider } from '@mui/material/styles';
import { createRoot } from 'react-dom/client';
import { Provider } from 'react-redux';
import { store } from './store';
import App from './component/App';

declare const module: { hot?: { accept: ( path: string, cb: () => void ) => void } };

const rootEl = document.getElementById('app') as HTMLElement;
const root = createRoot(rootEl);

const theme = createTheme({
  palette: {
    mode: 'dark',
    primary: {
      main: '#5893df',
    },
    secondary: {
      main: '#2ec5d3',
    },
    background: {
      default: '#192231',
      paper: '#24344d',
    },
  },
});

root.render(
  <Provider store={ store }>
    <ThemeProvider theme={ theme }>
      <App />
    </ThemeProvider>
  </Provider>
);

if (module.hot) {
  module.hot.accept('./component/App', () => {
    import('./component/App').then(({ default: NextApp }) => {
      root.render(
        <Provider store={ store }>
          <ThemeProvider theme={ theme }>
            <NextApp />
          </ThemeProvider>
        </Provider>
      );
    });
  });
}
