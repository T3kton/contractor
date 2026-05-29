import React, { useCallback, useEffect, useState } from 'react';
import { useSelector, useDispatch } from 'react-redux';
import ConfigDialog from './ConfigDialog';
import ErrorPanel from './ErrorPanel';
import { contractor } from '../store';
import { fetchStructureList, fetchStructure } from '../store/structuresSlice';
import { Box, Chip, CircularProgress, Link, Table, TableBody, TableCell, TableHead, TablePagination, TableRow, Typography } from '@mui/material';
import { Link as RouterLink } from 'react-router-dom';
import type { RootState, AppDispatch } from '../store';
import { dateStr, configValues, stateColor } from '../lib/utils';

interface Props {
  id?: string;
  site?: string;
}

const Structure: React.FC<Props> = ( { id, site } ) =>
{
  const dispatch = useDispatch<AppDispatch>();
  const authenticated = useSelector( ( s: RootState ) => s.app.authenticated );
  const { list, detail, loading, error } = useSelector( ( s: RootState ) => s.structures );
  const [page, setPage] = useState( 0 );
  const [rowsPerPage, setRowsPerPage] = useState( 25 );

  const fetchData = useCallback( () =>
  {
    if ( !authenticated ) return;
    if ( id !== undefined ) dispatch( fetchStructure( id ) );
    else dispatch( fetchStructureList( site ?? '' ) );
  }, [authenticated, dispatch, id, site] );

  useEffect( () => { fetchData(); }, [fetchData] );

  if ( loading ) return <Box sx={{ display: 'flex', justifyContent: 'center', mt: 4 }}><CircularProgress /></Box>;
  if ( error ) return <ErrorPanel error={ error } onRetry={ fetchData } />;

  if ( id !== undefined )
  {
    const d = detail;
    return (
      <Box>
        <Link component={ RouterLink } to="/structures">&larr; Structures</Link>
        <Typography variant="h5" gutterBottom>Structure Detail</Typography>
        { d !== null &&
          <Box>
            <ConfigDialog getConfig={ () => contractor.Building_Structure_call_getConfig( parseInt( id ) ) } />
            <Table size="small" sx={{ mt: 1 }}>
              <TableBody>
                <TableRow><TableCell variant="head">Site</TableCell><TableCell><Link component={ RouterLink } to={ '/site/' + d.structure.site?.toString() }>{ d.structure.site?.toString() }</Link></TableCell></TableRow>
                <TableRow><TableCell variant="head">Foundation</TableCell><TableCell><Link component={ RouterLink } to={ '/foundation/' + d.structure.foundation?.toString() }>{ d.structure.foundation?.toString() }</Link></TableCell></TableRow>
                <TableRow><TableCell variant="head">Hostname</TableCell><TableCell>{ d.structure.hostname }</TableCell></TableRow>
                <TableRow><TableCell variant="head">State</TableCell><TableCell>{ d.structure.state }</TableCell></TableRow>
                <TableRow><TableCell variant="head">Blueprint</TableCell><TableCell><Link component={ RouterLink } to={ '/blueprint/s/' + d.structure.blueprint?.toString() }>{ d.structure.blueprint?.toString() }</Link></TableCell></TableRow>
                <TableRow><TableCell variant="head">Config UUID</TableCell><TableCell>{ d.structure.config_uuid }</TableCell></TableRow>
                <TableRow>
                  <TableCell variant="head">Config Values</TableCell>
                  <TableCell>
                    <Table size="small">
                      <TableBody>
                        { configValues( d.structure.config_values ).map( ( item, index ) => (
                          <TableRow key={ index }>
                            <TableCell variant="head">{ item[0] }</TableCell>
                            <TableCell>{ item[1] }</TableCell>
                          </TableRow>
                        ) ) }
                      </TableBody>
                    </Table>
                  </TableCell>
                </TableRow>
                <TableRow><TableCell variant="head">Created</TableCell><TableCell>{ dateStr( d.structure.created ) }</TableCell></TableRow>
                <TableRow><TableCell variant="head">Updated</TableCell><TableCell>{ dateStr( d.structure.updated ) }</TableCell></TableRow>
                <TableRow><TableCell variant="head">Built At</TableCell><TableCell>{ dateStr( d.structure.built_at ) }</TableCell></TableRow>
              </TableBody>
            </Table>
            <Typography variant="h6" sx={{ mt: 2 }}>IP Addresses</Typography>
            <Table size="small">
              <TableHead>
                <TableRow>
                  <TableCell>Offset</TableCell>
                  <TableCell>Ip Address</TableCell>
                  <TableCell>Interface</TableCell>
                  <TableCell>Address Block</TableCell>
                  <TableCell>Created</TableCell>
                  <TableCell>Updated</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                { ( d.addresses || [] ).map( ( addr ) => (
                  <TableRow key={ addr.id }>
                    <TableCell>{ addr.offset }</TableCell>
                    <TableCell>{ addr.ip_address }</TableCell>
                    <TableCell>{ addr.interface_name }</TableCell>
                    <TableCell><Link component={ RouterLink } to={ '/addressblock/' + addr.address_block?.toString() }>{ addr.address_block?.toString() }</Link></TableCell>
                    <TableCell>{ dateStr( addr.created ) }</TableCell>
                    <TableCell>{ dateStr( addr.updated ) }</TableCell>
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
            <TableCell>Hostname</TableCell>
            <TableCell>State</TableCell>
            <TableCell>Created</TableCell>
            <TableCell>Updated</TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          { pageRows.map( ( item ) => (
            <TableRow key={ item.id }>
              <TableCell align="right"><Link component={ RouterLink } to={ '/structure/' + item.id }>{ item.id }</Link></TableCell>
              <TableCell>{ item.hostname }</TableCell>
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

export default Structure;
