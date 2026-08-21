import React, { useCallback, useEffect, useState } from 'react';
import { useSelector, useDispatch } from 'react-redux';
import ConfigDialog from './ConfigDialog';
import ErrorPanel from './ErrorPanel';
import { contractor } from '../store';
import { fetchFoundationList, fetchFoundation } from '../store/foundationsSlice';
import { DEFAULT_PAGE_SIZE } from '../store/sliceFactory';
import { Box, Chip, CircularProgress, IconButton, Link, Table, TableBody, TableCell, TableHead, TablePagination, TableRow, Typography } from '@mui/material';
import Visibility from '@mui/icons-material/Visibility';
import VisibilityOff from '@mui/icons-material/VisibilityOff';
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
  const updateVersion = useSelector( ( s: RootState ) => s.app.updateVersion );
  const { list, total, detail, loading, error } = useSelector( ( s: RootState ) => s.foundations );
  const [page, setPage] = useState( 0 );
  const [rowsPerPage, setRowsPerPage] = useState( DEFAULT_PAGE_SIZE );
  const [revealed, setRevealed] = useState<Record<string, boolean>>( {} );

  const fetchData = useCallback( () =>
  {
    if ( !authenticated ) return;
    if ( id !== undefined ) dispatch( fetchFoundation( id ) );
    else dispatch( fetchFoundationList( { site: site ?? '', position: page * rowsPerPage, count: rowsPerPage } ) );
  }, [authenticated, dispatch, id, site, page, rowsPerPage, updateVersion] );

  useEffect( () => { setPage( 0 ); }, [site] );
  useEffect( () => { setRevealed( {} ); }, [id] );  // don't carry a revealed secret to the next foundation
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
                <TableRow><TableCell variant="head">State</TableCell><TableCell><Chip size="small" label={ d.foundation.state } color={ stateColor( d.foundation.state ?? '' ) } /></TableCell></TableRow>
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
            { d.attributes.length > 0 &&
              <Box>
                <Typography variant="h6" sx={{ mt: 2 }}>{ d.foundation.type } Attributes</Typography>
                <Table size="small">
                  <TableBody>
                    { d.attributes.map( ( attr ) => (
                      <TableRow key={ attr.name }>
                        <TableCell variant="head">{ attr.name }</TableCell>
                        <TableCell>
                          { attr.secret && !revealed[ attr.name ] ? '••••••••' : attr.value }
                          { attr.secret &&
                            <IconButton
                              size="small"
                              sx={{ ml: 1 }}
                              aria-label={ ( revealed[ attr.name ] ? 'Hide ' : 'Show ' ) + attr.name }
                              onClick={ () => setRevealed( ( s ) => ( { ...s, [ attr.name ]: !s[ attr.name ] } ) ) }
                            >
                              { revealed[ attr.name ] ? <VisibilityOff fontSize="inherit" /> : <Visibility fontSize="inherit" /> }
                            </IconButton>
                          }
                        </TableCell>
                      </TableRow>
                    ) ) }
                  </TableBody>
                </Table>
              </Box>
            }
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
                    <TableCell><Chip size="small" label={ dep.state } color={ stateColor( dep.state ?? '' ) } /></TableCell>
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
          { ( list || [] ).map( ( item ) => (
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

export default Foundation;
