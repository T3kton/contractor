import React from 'react';
import CInP from './cinp';
import { Table, TableHead, TableRow, TableCell } from 'react-toolbox';

class JobLog extends React.Component
{
  state = {
      joblog_list: []
  };

  componentDidMount()
  {
    this.update( this.props );
  }

  componentWillReceiveProps( newProps )
  {
    this.setState( { joblog_list: [] } );
    this.update( newProps );
  }

  update( props )
  {
    props.listGet( props.site )
      .then( ( result ) =>
      {
        var joblog_list = [];
        for ( var id in result.data )
        {
          var joblog = result.data[ id ];
          id = CInP.extractIds( id )[0];
          joblog_list.push( { id: id,
                            job_id: joblog.job_id,
                            site: joblog.site,
                            target_class: joblog.target_class,
                            target_description: joblog.target_description,
                            script_name: joblog.script_name,
                            creator: joblog.creator,
                            start_finish: joblog.start_finish,
                            at: joblog.at,
                          } );
        }

        this.setState( { joblog_list: joblog_list } );
      } );
  }

  render()
  {
    return (
      <Table selectable={ false } multiSelectable={ false }>
        <TableHead>
          <TableCell>Job Id</TableCell>
          <TableCell>Site</TableCell>
          <TableCell>Target Class</TableCell>
          <TableCell>Target Description</TableCell>
          <TableCell>Script Name</TableCell>
          <TableCell>Creator</TableCell>
          <TableCell>Start/Finish</TableCell>
          <TableCell>At</TableCell>
        </TableHead>
        { this.state.joblog_list.map( ( item ) => (
          <TableRow key={ item.id } >
            <TableCell>{ item.job_id }</TableCell>
            <TableCell>{ item.site }</TableCell>
            <TableCell>{ item.target_class }</TableCell>
            <TableCell>{ item.target_description }</TableCell>
            <TableCell>{ item.script_name }</TableCell>
            <TableCell>{ item.creator }</TableCell>
            <TableCell>{ item.start_finish ? 'start' : 'finish' }</TableCell>
            <TableCell>{ item.at }</TableCell>
          </TableRow>
        ) ) }
      </Table>
    );

  }
};

export default JobLog;
