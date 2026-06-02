import React, { useCallback, useEffect } from 'react';
import { useSelector, useDispatch } from 'react-redux';
import ConfigDialog from './ConfigDialog';
import ScriptDialog from './ScriptDialog';
import ErrorPanel from './ErrorPanel';
import { contractor } from '../store';
import { fetchFoundationBluePrintList, fetchStructureBluePrintList, fetchFoundationBluePrint, fetchStructureBluePrint } from '../store/blueprintsSlice';
import type { BluePrint_FoundationBluePrint } from '../lib/Contractor';
import { Box, CircularProgress, Link, Table, TableBody, TableCell, TableHead, TableRow, Typography } from '@mui/material';
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
  const { listF, listS, detail, loading, error } = useSelector( ( s: RootState ) => s.blueprints );

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
      dispatch( fetchFoundationBluePrintList() );
      dispatch( fetchStructureBluePrintList() );
    }
  }, [authenticated, dispatch, id, blueprintType] );

  useEffect( () => { fetchData(); }, [fetchData] );

  if ( loading ) return <Box sx={{ display: 'flex', justifyContent: 'center', mt: 4 }}><CircularProgress /></Box>;
  if ( error ) return <ErrorPanel error={ error } onRetry={ fetchData } />;

  if ( id !== undefined )
  {
    const isFoundation = blueprintType === 'foundation';
    const fbp = isFoundation ? detail as BluePrint_FoundationBluePrint | null : null;
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
                { ( fbp as any )?.foundation_blueprint_list !== undefined &&
                  <TableRow>
                    <TableCell variant="head">Foundation Blueprint</TableCell>
                    <TableCell><ul>
                      { ( ( fbp as any ).foundation_blueprint_list || [] ).map( ( item: any, index: number ) => {
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
    </Box>
  );
};

export default BluePrint;
