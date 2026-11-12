import React, { useCallback, useEffect, useState } from 'react';
import { useSelector, useDispatch } from 'react-redux';
import ErrorPanel from './ErrorPanel';
import { fetchDependencyList, fetchDependency } from '../store/dependenciesSlice';
import { DEFAULT_PAGE_SIZE } from '../store/sliceFactory';
import { Box, Chip, CircularProgress, Link, Table, TableBody, TableCell, TableHead, TablePagination, TableRow, Typography } from '@mui/material';
import { Link as RouterLink } from 'react-router-dom';
import type { RootState, AppDispatch } from '../store';
import { dateStr, stateColor } from '../lib/utils';

interface Props {
  id?: string;
  site?: string;
}

const Dependency: React.FC<Props> = ( { id, site } ) =>
{
  const dispatch = useDispatch<AppDispatch>();
  const authenticated = useSelector( ( s: RootState ) => s.app.authenticated );
  const updateVersion = useSelector( ( s: RootState ) => s.app.updateVersion );
  const { list, total, detail, loading, error } = useSelector( ( s: RootState ) => s.dependencies );
  const [page, setPage] = useState( 0 );
  const [rowsPerPage, setRowsPerPage] = useState( DEFAULT_PAGE_SIZE );

  const fetchData = useCallback( () =>
  {
    if ( !authenticated ) return;
    if ( id !== undefined ) dispatch( fetchDependency( id ) );
    else dispatch( fetchDependencyList( { site: site ?? '', position: page * rowsPerPage, count: rowsPerPage } ) );
  }, [authenticated, dispatch, id, site, page, rowsPerPage, updateVersion] );

  useEffect( () => { setPage( 0 ); }, [site] );
  useEffect( () => { fetchData(); }, [fetchData] );

  if ( loading ) return <Box sx={{ display: 'flex', justifyContent: 'center', mt: 4 }}><CircularProgress /></Box>;
  if ( error ) return <ErrorPanel error={ error } onRetry={ fetchData } />;

  if ( id !== undefined )
  {
    return (
      <Box>
        <Link component={ RouterLink } to="/dependencies">&larr; Dependencies</Link>
        <Typography variant="h5" gutterBottom>Dependency Detail</Typography>
        { detail !== null &&
          <Table size="small" sx={{ mt: 1 }}>
            <TableBody>
              <TableRow><TableCell variant="head">Structure</TableCell><TableCell><Link component={ RouterLink } to={ '/structure/' + detail.structure?.toString() }>{ detail.structure?.toString() }</Link></TableCell></TableRow>
              <TableRow><TableCell variant="head">Dependency</TableCell><TableCell><Link component={ RouterLink } to={ '/dependency/' + detail.dependency?.toString() }>{ detail.dependency?.toString() }</Link></TableCell></TableRow>
              <TableRow><TableCell variant="head">Foundation</TableCell><TableCell><Link component={ RouterLink } to={ '/foundation/' + detail.foundation?.toString() }>{ detail.foundation?.toString() }</Link></TableCell></TableRow>
              <TableRow><TableCell variant="head">Script Structure</TableCell><TableCell><Link component={ RouterLink } to={ '/structure/' + detail.script_structure?.toString() }>{ detail.script_structure?.toString() }</Link></TableCell></TableRow>
              <TableRow><TableCell variant="head">Create Script Name</TableCell><TableCell>{ detail.create_script_name }</TableCell></TableRow>
              <TableRow><TableCell variant="head">Destroy Script Name</TableCell><TableCell>{ detail.destroy_script_name }</TableCell></TableRow>
              <TableRow><TableCell variant="head">State</TableCell><TableCell><Chip size="small" label={ detail.state } color={ stateColor( detail.state ?? '' ) } /></TableCell></TableRow>
              <TableRow><TableCell variant="head">Link</TableCell><TableCell>{ detail.link }</TableCell></TableRow>
              <TableRow><TableCell variant="head">Created</TableCell><TableCell>{ dateStr( detail.created ) }</TableCell></TableRow>
              <TableRow><TableCell variant="head">Updated</TableCell><TableCell>{ dateStr( detail.updated ) }</TableCell></TableRow>
              <TableRow><TableCell variant="head">Built At</TableCell><TableCell>{ dateStr( detail.built_at ) }</TableCell></TableRow>
            </TableBody>
          </Table>
        }
      </Box>
    );
  }

  return (
    <Box>
      <Table>
        <TableHead>
          <TableRow>
            <TableCell align="right">Id</TableCell>
            <TableCell>Foundation</TableCell>
            <TableCell>Structure</TableCell>
            <TableCell>State</TableCell>
            <TableCell>Created</TableCell>
            <TableCell>Updated</TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          { ( list || [] ).map( ( item ) => (
            <TableRow key={ item.id }>
              <TableCell align="right"><Link component={ RouterLink } to={ '/dependency/' + item.id }>{ item.id }</Link></TableCell>
              <TableCell>{ item.foundation }</TableCell>
              <TableCell>{ item.structure }</TableCell>
              <TableCell><Chip size="small" label={ item.state } color={ stateColor( item.state ) } /></TableCell>
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

export default Dependency;
