import React, { useCallback, useEffect, useState } from 'react';
import { useSelector, useDispatch } from 'react-redux';
import ErrorPanel from './ErrorPanel';
import { fetchComplexList, fetchComplex } from '../store/complexesSlice';
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

const Complex: React.FC<Props> = ( { id, site } ) =>
{
  const dispatch = useDispatch<AppDispatch>();
  const authenticated = useSelector( ( s: RootState ) => s.app.authenticated );
  const updateVersion = useSelector( ( s: RootState ) => s.app.updateVersion );
  const { list, total, detail, loading, error } = useSelector( ( s: RootState ) => s.complexes );
  const [page, setPage] = useState( 0 );
  const [rowsPerPage, setRowsPerPage] = useState( DEFAULT_PAGE_SIZE );
  const [revealed, setRevealed] = useState<Record<string, boolean>>( {} );

  const fetchData = useCallback( () =>
  {
    if ( !authenticated ) return;
    if ( id !== undefined ) dispatch( fetchComplex( id ) );
    else dispatch( fetchComplexList( { site: site ?? '', position: page * rowsPerPage, count: rowsPerPage } ) );
  }, [authenticated, dispatch, id, site, page, rowsPerPage, updateVersion] );

  useEffect( () => { setPage( 0 ); }, [site] );
  useEffect( () => { setRevealed( {} ); }, [id] );  // don't carry a revealed secret to the next complex
  useEffect( () => { fetchData(); }, [fetchData] );

  if ( loading ) return <Box sx={{ display: 'flex', justifyContent: 'center', mt: 4 }}><CircularProgress /></Box>;
  if ( error ) return <ErrorPanel error={ error } onRetry={ fetchData } />;

  if ( id !== undefined )
  {
    return (
      <Box>
        <Link component={ RouterLink } to="/complexes">&larr; Complexes</Link>
        <Typography variant="h5" gutterBottom>Complex Detail</Typography>
        { detail !== null &&
          <Box>
            <Table size="small" sx={{ mt: 1 }}>
              <TableBody>
                <TableRow><TableCell variant="head">Site</TableCell><TableCell><Link component={ RouterLink } to={ '/site/' + detail.complex.site?.toString() }>{ detail.complex.site?.toString() }</Link></TableCell></TableRow>
                <TableRow><TableCell variant="head">Description</TableCell><TableCell>{ detail.complex.description }</TableCell></TableRow>
                <TableRow><TableCell variant="head">Name</TableCell><TableCell>{ detail.complex.name }</TableCell></TableRow>
                <TableRow><TableCell variant="head">State</TableCell><TableCell><Chip size="small" label={ detail.complex.state } color={ stateColor( detail.complex.state ?? '' ) } /></TableCell></TableRow>
                <TableRow><TableCell variant="head">Type</TableCell><TableCell>{ detail.complex.type }</TableCell></TableRow>
                <TableRow><TableCell variant="head">Members</TableCell><TableCell><ul>{ ( detail.complex.members || [] ).map( ( item, index ) => (
                  <li key={ index }>{ item.toString() }</li>
                ) ) }</ul></TableCell></TableRow>
                <TableRow><TableCell variant="head">Built at Percentage</TableCell><TableCell>{ detail.complex.built_percentage }%</TableCell></TableRow>
                <TableRow><TableCell variant="head">Created</TableCell><TableCell>{ dateStr( detail.complex.created ) }</TableCell></TableRow>
                <TableRow><TableCell variant="head">Updated</TableCell><TableCell>{ dateStr( detail.complex.updated ) }</TableCell></TableRow>
              </TableBody>
            </Table>
            { detail.attributes.length > 0 &&
              <Box>
                <Typography variant="h6" sx={{ mt: 2 }}>{ detail.complex.type } Attributes</Typography>
                <Table size="small">
                  <TableBody>
                    { detail.attributes.map( ( attr ) => (
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
            <TableCell>Description</TableCell>
            <TableCell>Type</TableCell>
            <TableCell>State</TableCell>
            <TableCell>Created</TableCell>
            <TableCell>Updated</TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          { ( list || [] ).map( ( item ) => (
            <TableRow key={ item.id }>
              <TableCell align="right"><Link component={ RouterLink } to={ '/complex/' + item.id }>{ item.id }</Link></TableCell>
              <TableCell>{ item.description }</TableCell>
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

export default Complex;
