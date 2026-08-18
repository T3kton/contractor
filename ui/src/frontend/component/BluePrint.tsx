import React, { useCallback, useEffect, useState } from 'react';
import { useSelector, useDispatch } from 'react-redux';
import ConfigDialog from './ConfigDialog';
import ScriptDialog from './ScriptDialog';
import ErrorPanel from './ErrorPanel';
import { contractor } from '../store';
import { fetchFoundationBluePrintList, fetchStructureBluePrintList, fetchFoundationBluePrint, fetchStructureBluePrint } from '../store/blueprintsSlice';
import { DEFAULT_PAGE_SIZE } from '../store/sliceFactory';
import type { BluePrint_FoundationBluePrint, BluePrint_StructureBluePrint } from '../lib/Contractor';
import { Box, CircularProgress, Link, Table, TableBody, TableCell, TableHead, TablePagination, TableRow, Typography } from '@mui/material';
import { Link as RouterLink } from 'react-router-dom';
import type { RootState, AppDispatch } from '../store';
import { dateStr, configValues } from '../lib/utils';

interface Props {
  id?: string;
  blueprintType?: string;
}

const BluePrint: React.FC<Props> = ( { id, blueprintType } ) =>
{
  const dispatch = useDispatch<AppDispatch>();
  const authenticated = useSelector( ( s: RootState ) => s.app.authenticated );
  const updateVersion = useSelector( ( s: RootState ) => s.app.updateVersion );
  const { listF, totalF, listS, totalS, detail, loading, error } = useSelector( ( s: RootState ) => s.blueprints );
  const [pageF, setPageF] = useState( 0 );
  const [rowsPerPageF, setRowsPerPageF] = useState( DEFAULT_PAGE_SIZE );
  const [pageS, setPageS] = useState( 0 );
  const [rowsPerPageS, setRowsPerPageS] = useState( DEFAULT_PAGE_SIZE );

  const fetchData = useCallback( () =>
  {
    if ( !authenticated ) return;
    if ( id !== undefined )
    {
      if ( blueprintType === 'foundation' ) dispatch( fetchFoundationBluePrint( id ) );
      else dispatch( fetchStructureBluePrint( id ) );
    }
    else
    {
      dispatch( fetchFoundationBluePrintList( { position: pageF * rowsPerPageF, count: rowsPerPageF } ) );
      dispatch( fetchStructureBluePrintList( { position: pageS * rowsPerPageS, count: rowsPerPageS } ) );
    }
  }, [authenticated, dispatch, id, blueprintType, pageF, rowsPerPageF, pageS, rowsPerPageS, updateVersion] );

  useEffect( () => { fetchData(); }, [fetchData] );

  if ( loading ) return <Box sx={{ display: 'flex', justifyContent: 'center', mt: 4 }}><CircularProgress /></Box>;
  if ( error ) return <ErrorPanel error={ error } onRetry={ fetchData } />;

  if ( id !== undefined )
  {
    const isFoundation = blueprintType === 'foundation';
    const fbp = isFoundation ? detail as BluePrint_FoundationBluePrint | null : null;
    const sbp = isFoundation ? null : detail as BluePrint_StructureBluePrint | null;  // foundation_blueprint_list is a StructureBluePrint field, ie. the foundations this structure can be built on
    return (
      <Box>
        <Link component={ RouterLink } to="/blueprints">&larr; BluePrints</Link>
        <Typography variant="h5" gutterBottom>BluePrint Detail</Typography>
        { detail !== null &&
          <Box>
            <ConfigDialog getConfig={ () => contractor.BluePrint_BluePrint_call_getConfig( id ) } />
            <Table size="small" sx={{ mt: 1 }}>
              <TableBody>
                <TableRow><TableCell variant="head">Name</TableCell><TableCell>{ detail.name }</TableCell></TableRow>
                <TableRow><TableCell variant="head">Parents</TableCell><TableCell><ul>{ ( detail.parent_list || [] ).map( ( parent: any, index: number ) => {
                  const parentStr = parent.toString();
                  const to = isFoundation ? '/blueprint/f/' + parentStr : '/blueprint/s/' + parentStr;
                  return ( <li key={ index }><Link component={ RouterLink } to={ to }>{ parentStr }</Link></li> );
                } ) }</ul></TableCell></TableRow>
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
                <TableRow><TableCell variant="head">Scripts</TableCell><TableCell><ul>{ Object.entries( detail.script_map || {} ).map( ( [ name, uri ] ) => {
                  const scriptId = String( uri ).split( ':' )[ 1 ] ?? String( uri );
                  return ( <li key={ name }>{ name } <ScriptDialog getScript={ ( sid: string ) => contractor.BluePrint_Script_get( sid ) } id={ scriptId }/></li> );
                } ) }</ul></TableCell></TableRow>
                { sbp?.foundation_blueprint_list !== undefined &&
                  <TableRow>
                    <TableCell variant="head">Foundation Blueprints</TableCell>
                    <TableCell><ul>
                      { ( sbp.foundation_blueprint_list || [] ).map( ( item: any, index: number ) => {
                        const bpId = item.toString();
                        return ( <li key={ index }><Link component={ RouterLink } to={ '/blueprint/f/' + bpId }>{ bpId }</Link></li> );
                      } ) }
                    </ul></TableCell>
                  </TableRow>
                }
                { ( fbp as any )?.foundation_type_list !== undefined &&
                  <TableRow><TableCell variant="head">Type List</TableCell><TableCell>{ ( fbp as any ).foundation_type_list }</TableCell></TableRow>
                }
                { ( fbp as any )?.physical_interface_names !== undefined &&
                  <TableRow><TableCell variant="head">Physical Interface Names</TableCell><TableCell>{ ( fbp as any ).physical_interface_names }</TableCell></TableRow>
                }
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
    <Box>
      <Typography variant="h5" gutterBottom>Foundation BluePrints</Typography>
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
          { ( listF || [] ).map( ( item ) => (
            <TableRow key={ item.name }>
              <TableCell><Link component={ RouterLink } to={ '/blueprint/f/' + item.name }>{ item.name }</Link></TableCell>
              <TableCell>{ item.description }</TableCell>
              <TableCell>{ item.created }</TableCell>
              <TableCell>{ item.updated }</TableCell>
            </TableRow>
          ) ) }
        </TableBody>
      </Table>
      <TablePagination
        component="div"
        count={ totalF }
        page={ pageF }
        rowsPerPage={ rowsPerPageF }
        rowsPerPageOptions={ [25, 50, 100] }
        onPageChange={ ( _, p ) => setPageF( p ) }
        onRowsPerPageChange={ ( e ) => { setRowsPerPageF( parseInt( e.target.value, 10 ) ); setPageF( 0 ); } }
      />
      <Typography variant="h5" gutterBottom sx={{ mt: 2 }}>Structure BluePrints</Typography>
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
          { ( listS || [] ).map( ( item ) => (
            <TableRow key={ item.name }>
              <TableCell><Link component={ RouterLink } to={ '/blueprint/s/' + item.name }>{ item.name }</Link></TableCell>
              <TableCell>{ item.description }</TableCell>
              <TableCell>{ item.created }</TableCell>
              <TableCell>{ item.updated }</TableCell>
            </TableRow>
          ) ) }
        </TableBody>
      </Table>
      <TablePagination
        component="div"
        count={ totalS }
        page={ pageS }
        rowsPerPage={ rowsPerPageS }
        rowsPerPageOptions={ [25, 50, 100] }
        onPageChange={ ( _, p ) => setPageS( p ) }
        onRowsPerPageChange={ ( e ) => { setRowsPerPageS( parseInt( e.target.value, 10 ) ); setPageS( 0 ); } }
      />
    </Box>
  );
};

export default BluePrint;
