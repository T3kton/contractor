import React, { useCallback, useEffect } from 'react';
import { useSelector, useDispatch } from 'react-redux';
import ConfigDialog from './ConfigDialog';
import ErrorPanel from './ErrorPanel';
import { contractor } from '../store';
import { fetchSiteList, fetchSite } from '../store/sitesSlice';
import { Box, CircularProgress, Link, Table, TableBody, TableCell, TableHead, TableRow, Typography } from '@mui/material';
import { Link as RouterLink } from 'react-router-dom';
import type { RootState, AppDispatch } from '../store';
import { dateStr, configValues } from '../lib/utils';

interface Props {
  id?: string;
}

const Site: React.FC<Props> = ( { id } ) =>
{
  const dispatch = useDispatch<AppDispatch>();
  const authenticated = useSelector( ( s: RootState ) => s.app.authenticated );
  const { list, detail, loading, error } = useSelector( ( s: RootState ) => s.sites );

  const fetchData = useCallback( () =>
  {
    if ( !authenticated ) return;
    if ( id !== undefined ) dispatch( fetchSite( id ) );
    else dispatch( fetchSiteList() );
  }, [authenticated, dispatch, id] );

  useEffect( () => { fetchData(); }, [fetchData] );

  if ( loading ) return <Box sx={{ display: 'flex', justifyContent: 'center', mt: 4 }}><CircularProgress /></Box>;
  if ( error ) return <ErrorPanel error={ error } onRetry={ fetchData } />;

  if ( id !== undefined )
  {
    return (
      <Box>
        <Link component={ RouterLink } to="/sites">&larr; Sites</Link>
        <Typography variant="h5" gutterBottom>Site Detail</Typography>
        { detail !== null &&
          <Box>
            <ConfigDialog getConfig={ () => contractor.Site_Site_call_getConfig( id ) } />
            <Table size="small" sx={{ mt: 1 }}>
              <TableBody>
                <TableRow><TableCell variant="head">Name</TableCell><TableCell>{ detail.name }</TableCell></TableRow>
                <TableRow><TableCell variant="head">Parent</TableCell><TableCell><Link component={ RouterLink } to={ '/site/' + detail.parent?.toString() }>{ detail.parent?.toString() }</Link></TableCell></TableRow>
                <TableRow><TableCell variant="head">Description</TableCell><TableCell>{ detail.description }</TableCell></TableRow>
                <TableRow>
                  <TableCell variant="head">Config Values</TableCell>
                  <TableCell>
                    <Table size="small">
                      <TableBody>
                        { configValues( detail.config_values ).map( ( value ) => (
                          <TableRow key={ value[0] }>
                            <TableCell variant="head">{ value[0] }</TableCell>
                            <TableCell>{ value[1] }</TableCell>
                          </TableRow>
                        ) ) }
                      </TableBody>
                    </Table>
                  </TableCell>
                </TableRow>
                <TableRow><TableCell variant="head">Created</TableCell><TableCell>{ dateStr( detail.created ) }</TableCell></TableRow>
                <TableRow><TableCell variant="head">Updated</TableCell><TableCell>{ dateStr( detail.updated ) }</TableCell></TableRow>
              </TableBody>
            </Table>
          </Box>
        }
      </Box>
    );
  }

  return (
    <Table>
      <TableHead>
        <TableRow>
          <TableCell>Name</TableCell>
          <TableCell>Description</TableCell>
          <TableCell>Created</TableCell>
          <TableCell>Updated</TableCell>
        </TableRow>
      </TableHead>
      <TableBody>
        { ( list || [] ).map( ( item ) => (
          <TableRow key={ item.name }>
            <TableCell><Link component={ RouterLink } to={ '/site/' + item.name }>{ item.name }</Link></TableCell>
            <TableCell>{ item.description }</TableCell>
            <TableCell>{ item.created }</TableCell>
            <TableCell>{ item.updated }</TableCell>
          </TableRow>
        ) ) }
      </TableBody>
    </Table>
  );
};

export default Site;
