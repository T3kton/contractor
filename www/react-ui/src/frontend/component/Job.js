import React from 'react';
import CInP from './cinp';
import { Table, TableHead, TableRow, TableCell } from 'react-toolbox';
import { Link } from 'react-router-dom';


class AddressBlock extends React.Component
{
  state = {
      jobF_list: [],
      jobS_list: [],
      job: null
  };

  componentDidMount()
  {
    this.update( this.props );
  }

  componentWillReceiveProps( newProps )
  {
    this.setState( { jobF_list: [], jobS_list: [], job: null } );
    this.update( newProps );
  }

  update( props )
  {
    if( props.id !== undefined )
    {
      props.detailGet( props.id )
       .then( ( result ) =>
        {
          var data = result.data;
          data.site = CInP.extractIds( data.site )[0];
          if ( data.foundation !== undefined )
          {
            data.foundation = CInP.extractIds( data.foundation )[0];
          }
          if ( data.structure !== undefined )
          {
            data.structure = CInP.extractIds( data.structure )[0];
          }
          this.setState( { addressBlock: data } );
        } );
    }
    else
    {
      props.listGetS( props.site )
        .then( ( result ) =>
        {
          var job_list = [];
          for ( var id in result.data )
          {
            var job = result.data[ id ];
            id = CInP.extractIds( id )[0];
            job_list.push( { id: id,
                             script: job.script,
                             structure: job.structure,
                             message: job.message,
                             progress: job.progress,
                             state: job.state,
                             status: job.status,
                             created: job.created,
                             updated: job.updated,
                            } );
          }

          this.setState( { jobS_list: job_list } );
        } );
      props.listGetF( props.site )
        .then( ( result ) =>
        {
          var job_list = [];
          for ( var id in result.data )
          {
            var job = result.data[ id ];
            id = CInP.extractIds( id )[0];
            job_list.push( { id: id,
                             script: job.script,
                             foundation: job.foundation,
                             message: job.message,
                             progress: job.progress,
                             state: job.state,
                             status: job.status,
                             created: job.created,
                             updated: job.updated,
                            } );
          }

          this.setState( { jobF_list: job_list } );
        } );
    }
  }

  render()
  {
    if( this.props.id !== undefined )
    {
      var job = this.state.job;
      return (
        <div>
          <h1>Job Detail</h1>
          { job !== null &&
            <table>
              <thead/>
              <tbody>
                <tr><th>Site</th><td><Link to={ '/site/' + job.site }>{ job.site }</Link></td></tr>
                { job.foundation !== undefined &&
                  <tr><th>Foundation</th><td><Link to={ '/foundation/' + job.foundation }>{ job.foundation }</Link></td></tr>
                }
                { job.structure !== undefined &&
                  <tr><th>Structure</th><td><Link to={ '/structure/' + job.structure }>{ job.structure }</Link></td></tr>
                }
                <tr><th>Script</th><td>{ job.script_name }</td></tr>
                <tr><th>Message</th><td>{ job.message }</td></tr>
                <tr><th>Progress</th><td>{ job.progress }</td></tr>
                <tr><th>State</th><td>{ job.state }</td></tr>
                <tr><th>Status</th><td>{ job.status }</td></tr>
                <tr><th>Created</th><td>{ job.created }</td></tr>
                <tr><th>Updated</th><td>{ job.updated }</td></tr>
              </tbody>
            </table>
          }
        </div>
      );
    }

    return (
      <div>
        <h3>Foundation Jobs</h3>
        <Table selectable={ false } multiSelectable={ false }>
          <TableHead>
            <TableCell numeric>Id</TableCell>
            <TableCell>Script</TableCell>
            <TableCell>Foundation</TableCell>
            <TableCell>Message</TableCell>
            <TableCell>Progress</TableCell>
            <TableCell>State</TableCell>
            <TableCell>Status</TableCell>
            <TableCell>Created</TableCell>
            <TableCell>Updated</TableCell>
          </TableHead>
          { this.state.jobF_list.map( ( item, uri ) => (
            <TableRow key={ uri }>
              <TableCell numeric><Link to={ '/job/f/' + item.id }>{ item.id }</Link></TableCell>
              <TableCell>{ item.script }</TableCell>
              <TableCell>{ item.foundation }</TableCell>
              <TableCell>{ item.message }</TableCell>
              <TableCell>{ item.progress }</TableCell>
              <TableCell>{ item.state }</TableCell>
              <TableCell>{ item.status }</TableCell>
              <TableCell>{ item.created }</TableCell>
              <TableCell>{ item.updated }</TableCell>
            </TableRow>
          ) ) }
        </Table>
        <h3>Structure Jobs</h3>
        <Table selectable={ false } multiSelectable={ false }>
          <TableHead>
            <TableCell numeric>Id</TableCell>
            <TableCell>Script</TableCell>
            <TableCell>Structure</TableCell>
            <TableCell>Message</TableCell>
            <TableCell>Progress</TableCell>
            <TableCell>State</TableCell>
            <TableCell>Status</TableCell>
            <TableCell>Created</TableCell>
            <TableCell>Updated</TableCell>
          </TableHead>
          { this.state.jobS_list.map( ( item, uri ) => (
            <TableRow key={ uri }>
              <TableCell numeric><Link to={ '/job/s/' + item.id }>{ item.id }</Link></TableCell>
              <TableCell>{ item.script }</TableCell>
              <TableCell>{ item.structure }</TableCell>
              <TableCell>{ item.message }</TableCell>
              <TableCell>{ item.progress }</TableCell>
              <TableCell>{ item.state }</TableCell>
              <TableCell>{ item.status }</TableCell>
              <TableCell>{ item.created }</TableCell>
              <TableCell>{ item.updated }</TableCell>
            </TableRow>
          ) ) }
        </Table>
      </div>
    );

  }
};

export default AddressBlock;
