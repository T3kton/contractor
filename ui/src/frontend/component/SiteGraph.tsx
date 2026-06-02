import React, { useCallback, useEffect, useMemo } from 'react';
import { useSelector, useDispatch } from 'react-redux';
import ErrorPanel from './ErrorPanel';
import { fetchSiteGraph } from '../store/siteGraphSlice';
import { VisSingleContainer, VisGraph } from '@unovis/react';
import { GraphLayoutType, GraphNodeShape, GraphLinkArrowStyle } from '@unovis/ts';
import { Box, CircularProgress } from '@mui/material';
import type { RootState, AppDispatch } from '../store';

interface Props {
  site?: string;
}

const typeShape = ( n: any ): GraphNodeShape =>
{
  switch ( n.type )
  {
    case 'Structure': return GraphNodeShape.Circle;
    case 'Foundation': return GraphNodeShape.Square;
    case 'Complex': return GraphNodeShape.Hexagon;
    default: return GraphNodeShape.Triangle;
  }
};

const nodeStateColor = ( n: any ): string =>
{
  switch ( n.state )
  {
    case 'planned': return '#88FF88';
    case 'located': return '#8888FF';
    case 'built': return '#DDDDDD';
    default: return '#FF8888';
  }
};

const SiteGraph: React.FC<Props> = ( { site } ) =>
{
  const dispatch = useDispatch<AppDispatch>();
  const authenticated = useSelector( ( s: RootState ) => s.app.authenticated );
  const { graph, loading, error } = useSelector( ( s: RootState ) => s.siteGraph );

  const fetchData = useCallback( () =>
  {
    if ( !authenticated ) return;
    dispatch( fetchSiteGraph( site ?? '' ) );
  }, [authenticated, dispatch, site] );

  useEffect( () => { fetchData(); }, [fetchData] );

  const nodes = useMemo( () => ( graph?.nodes || [] ).map( ( n: any ) => ( { ...n } ) ), [graph] );
  const links = useMemo( () => ( graph?.edges || [] ).map( ( e: any ) => ( { source: e.from, target: e.to } ) ), [graph] );

  if ( loading ) return <Box sx={{ display: 'flex', justifyContent: 'center', mt: 4 }}><CircularProgress /></Box>;
  if ( error ) return <ErrorPanel error={ error } onRetry={ fetchData } />;

  return (
    <VisSingleContainer style={{ width: '100%' }} height={ 1000 }>
      <VisGraph
        data={{ nodes, links }}
        nodeLabel={ ( n: any ) => n.label }
        nodeIcon={ () => '' }
        nodeShape={ typeShape }
        nodeFill={ nodeStateColor }
        nodeStroke={ ( n: any ) => n.external ? '#DDDDDD' : '#FF0000' }
        nodeStrokeWidth={ ( n: any ) => n.has_job ? 3 : 1 }
        linkArrow={ GraphLinkArrowStyle.Single }
        layoutType={ GraphLayoutType.Dagre }
      />
    </VisSingleContainer>
  );
};

export default SiteGraph;
