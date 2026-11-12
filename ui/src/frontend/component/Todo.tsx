import React, { useCallback, useEffect, useState } from 'react';
import { useSelector, useDispatch } from 'react-redux';
import ErrorPanel from './ErrorPanel';
import { fetchFoundationClassList, fetchTodoList } from '../store/todoSlice';
import { DEFAULT_PAGE_SIZE } from '../store/sliceFactory';
import { Box, Checkbox, CircularProgress, FormControl, FormControlLabel, InputLabel, Link, MenuItem, Select, Table, TableBody, TableCell, TableHead, TablePagination, TableRow } from '@mui/material';
import { Link as RouterLink } from 'react-router-dom';
import type { RootState, AppDispatch } from '../store';

interface Props {
  site?: string;
}

const Todo: React.FC<Props> = ( { site } ) =>
{
  const dispatch = useDispatch<AppDispatch>();
  const authenticated = useSelector( ( s: RootState ) => s.app.authenticated );
  const updateVersion = useSelector( ( s: RootState ) => s.app.updateVersion );
  const { list, total, classList, loading, error } = useSelector( ( s: RootState ) => s.todo );
  const [hasDependencies, setHasDependencies] = useState( false );
  const [foundationClass, setFoundationClass] = useState( '' );
  const [page, setPage] = useState( 0 );
  const [rowsPerPage, setRowsPerPage] = useState( DEFAULT_PAGE_SIZE );

  useEffect( () =>
  {
    if ( !authenticated ) return;
    dispatch( fetchFoundationClassList() );
  }, [authenticated, dispatch, updateVersion] );

  const fetchData = useCallback( () =>
  {
    if ( !authenticated ) return;
    dispatch( fetchTodoList( { site: site ?? '', hasDependancies: hasDependencies, foundationClass: foundationClass || null, position: page * rowsPerPage, count: rowsPerPage } ) );
  }, [authenticated, dispatch, site, hasDependencies, foundationClass, page, rowsPerPage, updateVersion] );

  useEffect( () => { setPage( 0 ); }, [site, hasDependencies, foundationClass] );
  useEffect( () => { fetchData(); }, [fetchData] );

  if ( loading ) return <Box sx={{ display: 'flex', justifyContent: 'center', mt: 4 }}><CircularProgress /></Box>;
  if ( error ) return <ErrorPanel error={ error } onRetry={ fetchData } />;

  const classOptions: { value: string; label: string }[] = [
    { value: '', label: '<All>' },
    ...( classList || [] ).map( ( c ) => ( { value: c, label: c } ) ),
  ];

  return (
    <Box>
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2 }}>
        <FormControlLabel
          control={
            <Checkbox
              checked={ hasDependencies }
              onChange={ ( e ) => setHasDependencies( e.target.checked ) }
            />
          }
          label="Has Dependencies"
        />
        <FormControl size="small" sx={{ minWidth: 150 }}>
          <InputLabel>Foundation Class</InputLabel>
          <Select
            value={ foundationClass }
            onChange={ ( e ) => setFoundationClass( e.target.value ) }
            label="Foundation Class"
          >
            { classOptions.map( ( item ) => (
              <MenuItem key={ item.value } value={ item.value }>{ item.label }</MenuItem>
            ) ) }
          </Select>
        </FormControl>
      </Box>
      <Table>
        <TableHead>
          <TableRow>
            <TableCell align="right">Id</TableCell>
            <TableCell>Locator</TableCell>
            <TableCell>Num Dependants</TableCell>
            <TableCell>Complex</TableCell>
            <TableCell>Created</TableCell>
            <TableCell>Updated</TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          { ( list || [] ).map( ( item ) => (
            <TableRow key={ item.id }>
              <TableCell align="right"><Link component={ RouterLink } to={ '/foundation/' + item.id }>{ item.id }</Link></TableCell>
              <TableCell>{ item.locator }</TableCell>
              <TableCell>{ item.dependencyCount }</TableCell>
              <TableCell>{ item.complex }</TableCell>
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

export default Todo;
