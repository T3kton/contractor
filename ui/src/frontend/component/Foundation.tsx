import React, { useCallback, useEffect, useState } from 'react';
import { useSelector, useDispatch } from 'react-redux';
import ConfigDialog from './ConfigDialog';
import ErrorPanel from './ErrorPanel';
import { contractor } from '../store';
import { fetchFoundationList, fetchFoundation } from '../store/foundationsSlice';
import { Box, Chip, CircularProgress, Link, Table, TableBody, TableCell, TableHead, TablePagination, TableRow, Typography } from '@mui/material';
import { Link as RouterLink } from 'react-router-dom';
import type { RootState, AppDispatch } from '../store';
import { dateStr, stateColor } from '../lib/utils';

interface Props {
  id?: string;
  site?: string;
}

export const extractId = ( uri: string ): string => uri.split( ':' )[ 1 ];

const Foundation: React.FC<Props> = ( { id, site } ) =>
{
  const dispatch = useDispatch<AppDispatch>();
  const authenticated = useSelector( ( s: RootState ) => s.app.authenticated );
  const { list, detail, loading, error } = useSelector( ( s: RootState ) => s.foundations );
  const [page, setPage] = useState( 0 );
  const [rowsPerPage, setRowsPerPage] = useState( 25 );

  const fetchData = useCallback( () =>
  {
    if ( !authenticated ) return;
    if ( id !== undefined ) dispatch( fetchFoundation( id ) );
    else dispatch( fetchFoundationList( site ?? '' ) );
  }, [authenticated, dispatch, id, site] );

  useEffect( () => { fetchData(); }, [fetchData] );

  if ( loading ) return <Box sx={{ display: 'flex', justifyContent: 'center', mt: 4 }}><CircularProgress /></Box>;
  if ( error ) return <ErrorPanel error={ error } onRetry={ fetchData } />;

  if ( id !== undefined )
  {
    const d = detail;
    return (
      <Box>
        <Link component={ RouterLink } to="/foundations">&larr; Foundations</Link>
        <Typography variant="h5" gutterBottom>Foundation Detail</Typography>
        { d !== null &&
          <Box>
            <ConfigDialog getConfig={ () => contractor.Building_Foundation_call_getConfig( id ) } />
            <Table size="small" sx={{ mt: 1 }}>
              <TableBody>
                <TableRow><TableCell variant="head">Site</TableCell><TableCell><Link component={ RouterLink } to={ '/site/' + d.foundation.site?.toString() }>{ d.foundation.site?.toString() }</Link></TableCell></TableRow>
                <TableRow><TableCell variant="head">Locator</TableCell><TableCell>{ d.foundation.locator }</TableCell></TableRow>
                <TableRow><TableCell variant="head">State</TableCell><TableCell>{ d.foundation.state }</TableCell></TableRow>
                <TableRow><TableCell variant="head">Type</TableCell><TableCell>{ d.foundation.type }</TableCell></TableRow>
                <TableRow><TableCell variant="head">Blueprint</TableCell><TableCell><Link component={ RouterLink } to={ '/blueprint/f/' + d.foundation.blueprint?.toString() }>{ d.foundation.blueprint?.toString() }</Link></TableCell></TableRow>
                <TableRow><TableCell variant="head">Id Map</TableCell><TableCell>{ JSON.stringify( d.foundation.id_map ) }</TableCell></TableRow>
                <TableRow><TableCell variant="head">Class List</TableCell><TableCell>{ d.foundation.class_list }</TableCell></TableRow>
                <TableRow><TableCell variant="head">Created</TableCell><TableCell>{ dateStr( d.foundation.created ) }</TableCell></TableRow>
                <TableRow><TableCell variant="head">Updated</TableCell><TableCell>{ dateStr( d.foundation.updated ) }</TableCell></TableRow>
                <TableRow><TableCell variant="head">Located At</TableCell><TableCell>{ dateStr( d.foundation.located_at ) }</TableCell></TableRow>
                <TableRow><TableCell variant="head">Built At</TableCell><TableCell>{ dateStr( d.foundation.built_at ) }</TableCell></TableRow>
              </TableBody>
            </Table>
            <Typography variant="h6" sx={{ mt: 2 }}>Interfaces</Typography>
            <Table size="small">
              <TableHead>
                <TableRow>
                  <TableCell>Name</TableCell>
                  <TableCell>Physical Location</TableCell>
                  <TableCell>Provisioning</TableCell>
                  <TableCell>MAC</TableCell>
                  <TableCell>PXE</TableCell>
                  <TableCell>Network</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                { ( d.interface_list || [] ).map( ( item: any, index: number ) => (
                  <TableRow key={ index }>
                    <TableCell>{ item.name }</TableCell>
                    <TableCell>{ item.physical_location }</TableCell>
                    <TableCell>{ item.is_provisioning ? 'Yes' : 'No' }</TableCell>
                    <TableCell>{ item.mac }</TableCell>
                    <TableCell>{ item.pxe ? <Link component={ RouterLink } to={ '/pxe/' + extractId( item.pxe ) }>{ extractId( item.pxe ) }</Link> : '' }</TableCell>
                    <TableCell>{ item.network ? <Link component={ RouterLink } to={ '/network/' + extractId( item.network ) }>{ extractId( item.network ) }</Link> : '' }</TableCell>
                  </TableRow>
                ) ) }
              </TableBody>
            </Table>
            <Typography variant="h6" sx={{ mt: 2 }}>Depends on</Typography>
            <Table size="small">
              <TableHead>
                <TableRow>
                  <TableCell>Id</TableCell>
                  <TableCell>Foundation</TableCell>
                  <TableCell>Structure</TableCell>
                  <TableCell>Status</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                { ( d.dependencies || [] ).map( ( dep ) => (
                  <TableRow key={ dep.id }>
                    <TableCell><Link component={ RouterLink } to={ '/dependency/' + dep.id }>{ dep.id }</Link></TableCell>
                    <TableCell>{ dep.foundation?.toString() }</TableCell>
                    <TableCell>{ dep.structure?.toString() }</TableCell>
                    <TableCell>{ dep.state }</TableCell>
                  </TableRow>
                ) ) }
              </TableBody>
            </Table>
          </Box>
        }
      </Box>
    );
  }

  const rows = list || [];
  const pageRows = rows.slice( page * rowsPerPage, page * rowsPerPage + rowsPerPage );

  return (
    <Box>
      <Table>
        <TableHead>
          <TableRow>
            <TableCell align="right">Id</TableCell>
            <TableCell>Locator</TableCell>
            <TableCell>Site</TableCell>
            <TableCell>Type</TableCell>
            <TableCell>State</TableCell>
            <TableCell>Created</TableCell>
            <TableCell>Updated</TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          { pageRows.map( ( item ) => (
            <TableRow key={ item.id }>
              <TableCell align="right"><Link component={ RouterLink } to={ '/foundation/' + item.id }>{ item.id }</Link></TableCell>
              <TableCell>{ item.locator }</TableCell>
              <TableCell><Link component={ RouterLink } to={ '/site/' + item.site }>{ item.site }</Link></TableCell>
              <TableCell>{ item.type }</TableCell>
              <TableCell><Chip size="small" label={ item.state } color={ stateColor( item.state ) } /></TableCell>
              <TableCell>{ item.created }</TableCell>
              <TableCell>{ item.updated }</TableCell>
            </TableRow>
          ) ) }
        </TableBody>
      </Table>
      <TablePagination
        component="div"
        count={ rows.length }
        page={ page }
        rowsPerPage={ rowsPerPage }
        rowsPerPageOptions={ [10, 25, 50, 100] }
        onPageChange={ ( _, p ) => setPage( p ) }
        onRowsPerPageChange={ ( e ) => { setRowsPerPage( parseInt( e.target.value, 10 ) ); setPage( 0 ); } }
      />
    </Box>
  );
};

export default Foundation;
