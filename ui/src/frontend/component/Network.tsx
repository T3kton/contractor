import React, { useCallback, useEffect } from 'react';
import { useSelector, useDispatch } from 'react-redux';
import ErrorPanel from './ErrorPanel';
import { fetchNetworkList, fetchNetwork } from '../store/networksSlice';
import { Box, CircularProgress, Link, Table, TableBody, TableCell, TableHead, TableRow, Typography } from '@mui/material';
import { Link as RouterLink } from 'react-router-dom';
import type { RootState, AppDispatch } from '../store';
import { dateStr } from '../lib/utils';

interface Props {
  id?: string;
  site?: string;
}

const Network: React.FC<Props> = ( { id, site } ) =>
{
  const dispatch = useDispatch<AppDispatch>();
  const authenticated = useSelector( ( s: RootState ) => s.app.authenticated );
  const { list, detail, loading, error } = useSelector( ( s: RootState ) => s.networks );

  const fetchData = useCallback( () =>
  {
    if ( !authenticated ) return;
    if ( id !== undefined ) dispatch( fetchNetwork( id ) );
    else dispatch( fetchNetworkList( site ?? '' ) );
  }, [authenticated, dispatch, id, site] );

  useEffect( () => { fetchData(); }, [fetchData] );

  if ( loading ) return <Box sx={{ display: 'flex', justifyContent: 'center', mt: 4 }}><CircularProgress /></Box>;
  if ( error ) return <ErrorPanel error={ error } onRetry={ fetchData } />;

  if ( id !== undefined )
  {
    return (
      <Box>
        <Link component={ RouterLink } to="/networks">&larr; Networks</Link>
        <Typography variant="h5" gutterBottom>Network Detail</Typography>
        { detail !== null &&
          <Box>
            <Table size="small" sx={{ mt: 1 }}>
              <TableBody>
                <TableRow><TableCell variant="head">Site</TableCell><TableCell><Link component={ RouterLink } to={ '/site/' + detail.network.site?.toString() }>{ detail.network.site?.toString() }</Link></TableCell></TableRow>
                <TableRow><TableCell variant="head">Name</TableCell><TableCell>{ detail.network.name }</TableCell></TableRow>
                <TableRow><TableCell variant="head">MTU</TableCell><TableCell>{ detail.network.mtu }</TableCell></TableRow>
                <TableRow><TableCell variant="head">Created</TableCell><TableCell>{ dateStr( detail.network.created ) }</TableCell></TableRow>
                <TableRow><TableCell variant="head">Updated</TableCell><TableCell>{ dateStr( detail.network.updated ) }</TableCell></TableRow>
              </TableBody>
            </Table>
            <Typography variant="h6" sx={{ mt: 2 }}>Address Blocks</Typography>
            <Table size="small">
              <TableHead>
                <TableRow>
                  <TableCell>Address Block</TableCell>
                  <TableCell>Vlan</TableCell>
                  <TableCell>Created</TableCell>
                  <TableCell>Updated</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                { detail.networkAddressBlocks.map( ( nab ) => (
                  <TableRow key={ nab.id }>
                    <TableCell><Link component={ RouterLink } to={ '/addressblock/' + nab.address_block?.toString() }>{ nab.address_block?.toString() }</Link></TableCell>
                    <TableCell>{ nab.vlan }</TableCell>
                    <TableCell>{ dateStr( nab.created ) }</TableCell>
                    <TableCell>{ dateStr( nab.updated ) }</TableCell>
                  </TableRow>
                ) ) }
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
          <TableCell>Id</TableCell>
          <TableCell>Name</TableCell>
          <TableCell>Created</TableCell>
          <TableCell>Updated</TableCell>
        </TableRow>
      </TableHead>
      <TableBody>
        { ( list || [] ).map( ( item ) => (
          <TableRow key={ item.name }>
            <TableCell><Link component={ RouterLink } to={ '/network/' + item.id }>{ item.id }</Link></TableCell>
            <TableCell>{ item.name }</TableCell>
            <TableCell>{ item.created }</TableCell>
            <TableCell>{ item.updated }</TableCell>
          </TableRow>
        ) ) }
      </TableBody>
    </Table>
  );
};

export default Network;
