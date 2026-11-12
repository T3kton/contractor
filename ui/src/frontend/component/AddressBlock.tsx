import React, { useCallback, useEffect, useState } from 'react';
import { useSelector, useDispatch } from 'react-redux';
import ErrorPanel from './ErrorPanel';
import { fetchAddressBlockList, fetchAddressBlock } from '../store/addressBlocksSlice';
import { DEFAULT_PAGE_SIZE } from '../store/sliceFactory';
import { Box, CircularProgress, Link, Table, TableBody, TableCell, TableHead, TablePagination, TableRow, Typography } from '@mui/material';
import { Link as RouterLink } from 'react-router-dom';
import type { RootState, AppDispatch } from '../store';
import { dateStr } from '../lib/utils';

interface Props {
  id?: string;
  site?: string;
}

const AddressBlock: React.FC<Props> = ( { id, site } ) =>
{
  const dispatch = useDispatch<AppDispatch>();
  const authenticated = useSelector( ( s: RootState ) => s.app.authenticated );
  const updateVersion = useSelector( ( s: RootState ) => s.app.updateVersion );
  const { list, total, detail, loading, error } = useSelector( ( s: RootState ) => s.addressBlocks );
  const [page, setPage] = useState( 0 );
  const [rowsPerPage, setRowsPerPage] = useState( DEFAULT_PAGE_SIZE );

  const fetchData = useCallback( () =>
  {
    if ( !authenticated ) return;
    if ( id !== undefined ) dispatch( fetchAddressBlock( id ) );
    else dispatch( fetchAddressBlockList( { site: site ?? '', position: page * rowsPerPage, count: rowsPerPage } ) );
  }, [authenticated, dispatch, id, site, page, rowsPerPage, updateVersion] );

  useEffect( () => { setPage( 0 ); }, [site] );
  useEffect( () => { fetchData(); }, [fetchData] );

  if ( loading ) return <Box sx={{ display: 'flex', justifyContent: 'center', mt: 4 }}><CircularProgress /></Box>;
  if ( error ) return <ErrorPanel error={ error } onRetry={ fetchData } />;

  if ( id !== undefined )
  {
    const ab = detail?.addressBlock;
    return (
      <Box>
        <Link component={ RouterLink } to="/addressblocks">&larr; Address Blocks</Link>
        <Typography variant="h5" gutterBottom>Address Block Detail</Typography>
        { detail !== null && ab !== undefined &&
          <Box>
            <Table size="small" sx={{ mt: 1 }}>
              <TableBody>
                <TableRow><TableCell variant="head">Name</TableCell><TableCell>{ ab.name }</TableCell></TableRow>
                <TableRow><TableCell variant="head">Site</TableCell><TableCell><Link component={ RouterLink } to={ '/site/' + ab.site?.toString() }>{ ab.site?.toString() }</Link></TableCell></TableRow>
                <TableRow><TableCell variant="head">Subnet</TableCell><TableCell>{ ab.subnet }</TableCell></TableRow>
                <TableRow><TableCell variant="head">Prefix</TableCell><TableCell>{ ab.prefix }</TableCell></TableRow>
                <TableRow><TableCell variant="head">Gateway</TableCell><TableCell>{ ab.gateway }</TableCell></TableRow>
                <TableRow><TableCell variant="head">Netmask</TableCell><TableCell>{ ab.netmask }</TableCell></TableRow>
                <TableRow><TableCell variant="head">Size</TableCell><TableCell>{ ab.size }</TableCell></TableRow>
                <TableRow><TableCell variant="head">IsIPv4</TableCell><TableCell>{ String( ab.isIpV4 ) }</TableCell></TableRow>
                <TableRow><TableCell variant="head">Created</TableCell><TableCell>{ dateStr( ab.created ) }</TableCell></TableRow>
                <TableRow><TableCell variant="head">Updated</TableCell><TableCell>{ dateStr( ab.updated ) }</TableCell></TableRow>
              </TableBody>
            </Table>
            <Typography variant="h6" sx={{ mt: 2 }}>Addresses</Typography>
            <Table size="small">
              <TableHead><TableRow><TableCell>Offset</TableCell><TableCell>IP</TableCell><TableCell>Structure</TableCell><TableCell>Interface</TableCell><TableCell>Created</TableCell><TableCell>Updated</TableCell></TableRow></TableHead>
              <TableBody>
                { detail.addresses.map( ( addr ) => (
                  <TableRow key={ addr.id }>
                    <TableCell>{ addr.offset }</TableCell>
                    <TableCell>{ addr.ip_address }</TableCell>
                    <TableCell>{ addr.networked !== undefined &&
                      // Address relates to Networked, not Structure (there is no addr.structure, which is why this was blank).  Structure is Networked's only subclass and shares its id, so the id links straight through -- the hostname lives on Networked and would need a fetch per row to show.
                      <Link component={ RouterLink } to={ '/structure/' + addr.networked.toString() }>{ addr.networked.toString() }</Link>
                    }</TableCell>
                    <TableCell>{ addr.interface_name }</TableCell>
                    <TableCell>{ dateStr( addr.created ) }</TableCell>
                    <TableCell>{ dateStr( addr.updated ) }</TableCell>
                  </TableRow>
                ) ) }
              </TableBody>
            </Table>
            <Typography variant="h6" sx={{ mt: 2 }}>Reserved</Typography>
            <Table size="small">
              <TableHead><TableRow><TableCell>Offset</TableCell><TableCell>IP</TableCell><TableCell>Reason</TableCell><TableCell>Created</TableCell><TableCell>Updated</TableCell></TableRow></TableHead>
              <TableBody>
                { detail.reserved.map( ( r ) => (
                  <TableRow key={ r.id }><TableCell>{ r.offset }</TableCell><TableCell>{ r.ip_address }</TableCell><TableCell>{ r.reason }</TableCell><TableCell>{ dateStr( r.created ) }</TableCell><TableCell>{ dateStr( r.updated ) }</TableCell></TableRow>
                ) ) }
              </TableBody>
            </Table>
            <Typography variant="h6" sx={{ mt: 2 }}>Dynamic</Typography>
            <Table size="small">
              <TableHead><TableRow><TableCell>Offset</TableCell><TableCell>IP</TableCell><TableCell>Created</TableCell><TableCell>Updated</TableCell></TableRow></TableHead>
              <TableBody>
                { detail.dynamic.map( ( d ) => (
                  <TableRow key={ d.id }><TableCell>{ d.offset }</TableCell><TableCell>{ d.ip_address }</TableCell><TableCell>{ dateStr( d.created ) }</TableCell><TableCell>{ dateStr( d.updated ) }</TableCell></TableRow>
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
            <TableCell>Subnet</TableCell>
            <TableCell>Prefix</TableCell>
            <TableCell>Created</TableCell>
            <TableCell>Updated</TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          { ( list || [] ).map( ( item ) => (
            <TableRow key={ item.id }>
              <TableCell><Link component={ RouterLink } to={ '/addressblock/' + item.id }>{ item.name }</Link></TableCell>
              <TableCell>{ item.subnet }</TableCell>
              <TableCell>{ item.prefix }</TableCell>
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

export default AddressBlock;
