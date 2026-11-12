import React, { useCallback, useEffect, useState } from 'react';
import { useSelector, useDispatch } from 'react-redux';
import ErrorPanel from './ErrorPanel';
import { fetchDirectoryZoneList, fetchDirectoryZone, GLOBAL_ZONE_ID } from '../store/directorySlice';
import { DEFAULT_PAGE_SIZE } from '../store/sliceFactory';
import { Box, CircularProgress, Link, Table, TableBody, TableCell, TableHead, TablePagination, TableRow, Typography } from '@mui/material';
import { Link as RouterLink } from 'react-router-dom';
import type { RootState, AppDispatch } from '../store';
import { dateStr } from '../lib/utils';

interface Props {
  id?: string;
}

const Directory: React.FC<Props> = ( { id } ) =>
{
  const dispatch = useDispatch<AppDispatch>();
  const authenticated = useSelector( ( s: RootState ) => s.app.authenticated );
  const updateVersion = useSelector( ( s: RootState ) => s.app.updateVersion );
  const { list, total, detail, loading, error } = useSelector( ( s: RootState ) => s.directory );
  const [page, setPage] = useState( 0 );
  const [rowsPerPage, setRowsPerPage] = useState( DEFAULT_PAGE_SIZE );

  const fetchData = useCallback( () =>
  {
    if ( !authenticated ) return;
    if ( id !== undefined ) dispatch( fetchDirectoryZone( id ) );
    else dispatch( fetchDirectoryZoneList( { position: page * rowsPerPage, count: rowsPerPage } ) );
  }, [authenticated, dispatch, id, page, rowsPerPage, updateVersion] );

  useEffect( () => { fetchData(); }, [fetchData] );

  if ( loading ) return <Box sx={{ display: 'flex', justifyContent: 'center', mt: 4 }}><CircularProgress /></Box>;
  if ( error ) return <ErrorPanel error={ error } onRetry={ fetchData } />;

  if ( id !== undefined )
  {
    const isGlobal = id === GLOBAL_ZONE_ID;
    const zone = detail?.zone;
    return (
      <Box>
        <Link component={ RouterLink } to="/directory">&larr; Directory</Link>
        <Typography variant="h5" gutterBottom>{ isGlobal ? 'Global Entries' : 'Zone Detail' }</Typography>
        { detail !== null && ( isGlobal || zone !== undefined && zone !== null ) &&
          <Box>
            { !isGlobal && zone !== undefined && zone !== null &&
              <Table size="small" sx={{ mt: 1 }}>
                <TableBody>
                  <TableRow><TableCell variant="head">Name</TableCell><TableCell>{ zone.name }</TableCell></TableRow>
                  <TableRow><TableCell variant="head">FQDN</TableCell><TableCell>{ zone.fqdn }</TableCell></TableRow>
                  <TableRow><TableCell variant="head">Parent</TableCell><TableCell>{ zone.parent !== undefined && <Link component={ RouterLink } to={ '/directoryzone/' + zone.parent.toString() }>{ detail?.parentName ?? zone.parent.toString() }</Link> }</TableCell></TableRow>
                  <TableRow><TableCell variant="head">TTL</TableCell><TableCell>{ zone.ttl }</TableCell></TableRow>
                  <TableRow><TableCell variant="head">Refresh</TableCell><TableCell>{ zone.refresh }</TableCell></TableRow>
                  <TableRow><TableCell variant="head">Retry</TableCell><TableCell>{ zone.retry }</TableCell></TableRow>
                  <TableRow><TableCell variant="head">Expire</TableCell><TableCell>{ zone.expire }</TableCell></TableRow>
                  <TableRow><TableCell variant="head">Minimum</TableCell><TableCell>{ zone.minimum }</TableCell></TableRow>
                  <TableRow><TableCell variant="head">Created</TableCell><TableCell>{ dateStr( zone.created ) }</TableCell></TableRow>
                  <TableRow><TableCell variant="head">Updated</TableCell><TableCell>{ dateStr( zone.updated ) }</TableCell></TableRow>
                </TableBody>
              </Table>
            }
            <Typography variant="h6" sx={{ mt: 2 }}>Entries</Typography>
            <Table size="small">
              <TableHead>
                <TableRow>
                  <TableCell>Name</TableCell>
                  <TableCell>Type</TableCell>
                  <TableCell>Priority</TableCell>
                  <TableCell>Weight</TableCell>
                  <TableCell>Port</TableCell>
                  <TableCell>Target</TableCell>
                  <TableCell>Created</TableCell>
                  <TableCell>Updated</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                { detail.entries.map( ( entry ) => (
                  <TableRow key={ entry.id }>
                    <TableCell>{ entry.name }</TableCell>
                    <TableCell>{ entry.type }</TableCell>
                    <TableCell>{ entry.priority }</TableCell>
                    <TableCell>{ entry.weight }</TableCell>
                    <TableCell>{ entry.port }</TableCell>
                    <TableCell>{ entry.target }</TableCell>
                    <TableCell>{ dateStr( entry.created ) }</TableCell>
                    <TableCell>{ dateStr( entry.updated ) }</TableCell>
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
    <Box>
      <Table>
        <TableHead>
          <TableRow>
            <TableCell>Name</TableCell>
            <TableCell>FQDN</TableCell>
            <TableCell>Parent</TableCell>
            <TableCell>Created</TableCell>
            <TableCell>Updated</TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          <TableRow>
            <TableCell><Link component={ RouterLink } to={ '/directoryzone/' + GLOBAL_ZONE_ID }><em>Global</em></Link></TableCell>
            <TableCell colSpan={ 4 } />
          </TableRow>
          { ( list || [] ).map( ( item ) => (
            <TableRow key={ item.id }>
              <TableCell><Link component={ RouterLink } to={ '/directoryzone/' + item.id }>{ item.name }</Link></TableCell>
              <TableCell>{ item.fqdn }</TableCell>
              <TableCell>{ item.parent }</TableCell>
              <TableCell>{ item.created }</TableCell>
              <TableCell>{ item.updated }</TableCell>
            </TableRow>
          ) ) }
        </TableBody>
      </Table>
      <TablePagination
        component="div"
        count={ total }
        page={ page }
        rowsPerPage={ rowsPerPage }
        rowsPerPageOptions={ [25, 50, 100] }
        onPageChange={ ( _, p ) => setPage( p ) }
        onRowsPerPageChange={ ( e ) => { setRowsPerPage( parseInt( e.target.value, 10 ) ); setPage( 0 ); } }
      />
    </Box>
  );
};

export default Directory;
