import { createSlice } from '@reduxjs/toolkit';
import { createAuthThunk } from './sliceFactory';
import { Contractor, Site_Site } from '../lib/Contractor';

const stateColorMap: Record<string, string> = { 'planned': '#88FF88', 'located': '#8888FF', 'built': '#FFFFFF' };

export interface GraphNode {
  id: string;
  label: string;
  type: string;
  state: string;
  has_job: boolean;
  external: boolean;
}

export interface GraphEdge {
  from: string;
  to: string;
}

export interface SiteGraphData {
  nodes: GraphNode[];
  edges: GraphEdge[];
}

interface SiteGraphState {
  graph: SiteGraphData | null;
  loading: boolean;
  error: string | null;
}

export const fetchSiteGraph = createAuthThunk(
  'siteGraph/fetch',
  async ( site: string, contractor ) =>
  {
    const siteId = site ? new Site_Site( contractor, site ).toString() : '';
    const result = await contractor.Site_Site_call_getDependencyMap( siteId ) as Record<string, any>;
    var graph: SiteGraphData = { nodes: [], edges: [] };
    for ( var id in result )
    {
      var node = result[ id ];
      graph.nodes.push( { id, label: node.description, type: node.type, state: node.state, has_job: node.has_job, external: node.external } );
      for ( var i in node.dependency_list )
      {
        graph.edges.push( { from: node.dependency_list[ i ], to: id } );
      }
    }
    return graph;
  }
);

const siteGraphSlice = createSlice( {
  name: 'siteGraph',
  initialState: { graph: null, loading: false, error: null } as SiteGraphState,
  reducers: {
    invalidate: ( state ) => { state.graph = null; },
  },
  extraReducers: ( builder ) =>
  {
    builder
      .addCase( fetchSiteGraph.pending, ( state ) => { state.loading = true; state.error = null; } )
      .addCase( fetchSiteGraph.fulfilled, ( state, action ) => { state.loading = false; state.graph = action.payload; } )
      .addCase( fetchSiteGraph.rejected, ( state, action ) => { state.loading = false; state.error = ( ( action.payload as any )?.msg ) ?? action.error.message ?? 'Error loading data'; } );
  },
} );

export const { invalidate: invalidateSiteGraph } = siteGraphSlice.actions;
export default siteGraphSlice.reducer;
